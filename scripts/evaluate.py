"""Reproducible, *model-free* evaluation of MatchShift end-to-end behavior.

Not an accuracy benchmark on real Premier League play: the scenarios are
synthetic and scripted. The report measures data integrity, event grounding,
persona completeness, agent-stage execution, and safe failure recovery.
"""
import argparse
import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

from packages.agents.contracts import StoryRequest
from packages.agents.workflow import run_story
from packages.analytics.broadcast import build_cues
from packages.analytics.insights import generate_insights
from packages.analytics.metrics import build_possessions, snapshot_at
from packages.simulator.generator import DURATION, GOALS, generate_events

AUDIENCES=("fan","analyst","broadcast")
STAGES=("TacticalAnalyst","NarrativeDirector","EvidenceVerifier","AudienceAgent")
DEFAULT_SEEDS=(0,7,12,42,100,2026)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def evaluate_seed(seed: int) -> dict:
    """Validate a match's source semantics before interpreting the evidence."""
    events=generate_events(seed)
    require(len(events)==180, "Expected 180 half-minute events")
    require(events==generate_events(seed), "Seeded events are not deterministic")
    require(len({e.id for e in events})==len(events), "Duplicate event identifiers")
    require([e.second for e in events]==list(range(30,DURATION+1,30)), "Events not time-ordered")
    require([(e.second,e.team) for e in events if e.kind=="goal"]==list(GOALS.items()), "Scripted score inconsistent")
    possessions=build_possessions(events)
    require([eid for chain in possessions for eid in chain.event_ids]==[e.id for e in events],
            "Possession chains do not cover every source event")
    for second in (60,300,1800,4200):
        prefix=[e for e in events if e.second<=second]
        require(snapshot_at(events,second)==snapshot_at(prefix,second),
                f"Future leakage at t={second}")
    insights=generate_insights(events)
    cues=build_cues(events,insights,DURATION)
    require(len(cues)==len(insights), "A broadcast moment is missing a cue")
    by_id={event.id:event for event in events}
    for insight in insights:
        require(bool(insight.evidence_event_ids), f"Insight {insight.id} has no evidence")
        require(all(eid in by_id and by_id[eid].second<=insight.second
                    for eid in insight.evidence_event_ids),
                f"Insight {insight.id} cites future or missing evidence")
        if insight.kind=="tactical_shift":
            current=snapshot_at(events,insight.second)
            previous=snapshot_at(events,insight.second-300)
            delta=getattr(current,insight.team).high_regains-getattr(previous,insight.team).high_regains
            require(insight.metric_value==delta, "High-regain delta not reproducible")
    for cue in cues:
        source=next((i for i in insights if i.id==cue.insight_id),None)
        require(source is not None and cue.second==source.second
                and cue.evidence_event_ids==source.evidence_event_ids,
                f"Cue {cue.id} not grounded in an insight")
        require(cue.second<cue.until_second<=DURATION, "Broadcast timing out of range")

    digest=hashlib.sha256(json.dumps(
        [e.model_dump(mode="json") for e in events],
        sort_keys=True,separators=(",",":")
    ).encode()).hexdigest()
    return {
        "seed":seed,"events":len(events),"possessions":len(possessions),
        "goals":len([e for e in events if e.kind=="goal"]),
        "tactical_shift_insights":len([i for i in insights if i.kind=="tactical_shift"]),
        "insights":len(insights),"broadcast_cues":len(cues),
        "match_event_sha256":digest,
    }


async def evaluate_stories(seed: int) -> int:
    events=generate_events(seed)
    produced=0
    for insight in generate_insights(events):
        for audience in AUDIENCES:
            story=await run_story(StoryRequest(seed=seed,insight_id=insight.id,audience=audience))
            require(story.verified, "An unverified story escaped")
            require(story.source=="deterministic" and story.style_source=="deterministic",
                    "Deterministic evaluation attempted model inference")
            require(story.insight_id==insight.id and story.audience==audience,
                    "Wrong story identity or persona")
            require(story.evidence_event_ids==insight.evidence_event_ids,
                    "Story evidence changed during handoffs")
            require(tuple(step.stage for step in story.trace)==STAGES,
                    "Agent stages were not fully executed")
            require(story.trace[2].status=="approved",
                    "EvidenceVerifier did not approve the result")
            require(insight.explanation in story.narration,
                    "Verified observation dropped from narration")
            produced+=1
    return produced


async def evaluate_recovery(seed: int=7) -> dict:
    """Attack the two allowlisted model outputs and simulate a provider outage."""
    module=import_module("packages.agents.workflow")
    insight=next(i for i in generate_insights(generate_events(seed)) if i.kind=="goal")
    request=StoryRequest(seed=seed,insight_id=insight.id,audience="broadcast")

    async def unsafe_angle(_analysis):
        return "the referee gave an invented red card and 200 goals"
    async def permitted_angle(_analysis):
        return "scoreline"
    async def unsafe_style(_analysis,_audience):
        return "claim twenty-six fabricated goals"
    async def provider_down(_analysis):
        raise ConnectionError("Simulated local inference outage")

    with patch.dict(os.environ,{"MATCHSHIFT_INFERENCE":"foundry_local"}):
        with patch.object(module,"choose_with_foundry_local",unsafe_angle):
            rejected=await run_story(request)
        require(rejected.verified and rejected.source=="fallback",
                "Unsafe director output was not replaced")
        require(any(t.status=="rejected" for t in rejected.trace),
                "Unsafe director output did not leave a rejected trace")
        require("invented" not in rejected.narration,"Invented model claim was published")

        with patch.object(module,"choose_with_foundry_local",permitted_angle),\
             patch.object(module,"choose_style_with_foundry_local",unsafe_style):
            invalid_style=await run_story(request)
        require(invalid_style.verified and invalid_style.source=="foundry_local"
                and invalid_style.style_source=="fallback",
                "Invalid style proposal was not handled independently")
        require("fabricated" not in invalid_style.narration,
                "Unsafe style text was published")

        with patch.object(module,"choose_with_foundry_local",provider_down):
            outage=await run_story(request)
        require(outage.verified and outage.source=="fallback",
                "Provider outage did not recover")
        require(any(t.status=="fallback" for t in outage.trace),
                "Provider outage provenance not recorded")

    return {
        "invalid_director_angle_rejected":True,
        "invalid_audience_style_rejected":True,
        "provider_outage_recovered":True,
        "real_model_invoked":False,
    }


async def evaluate(seeds: tuple[int,...]=DEFAULT_SEEDS) -> dict:
    if os.getenv("MATCHSHIFT_INFERENCE","deterministic").lower()!="deterministic":
        raise RuntimeError("Deterministic evaluation cannot use live inference")
    require(bool(seeds) and len(set(seeds))==len(seeds),"Provide nonempty unique seeds")
    started=time.perf_counter()
    scenarios=[]
    story_count=0
    for seed in seeds:
        require(0<=seed<=1_000_000,"Invalid seed")
        result=evaluate_seed(seed)
        count=await evaluate_stories(seed)
        result["verified_persona_stories"]=count
        scenarios.append(result)
        story_count+=count
    recovery=await evaluate_recovery(seeds[0])
    return {
        "schema_version":"1",
        "evaluation_mode":"deterministic_offline",
        "dataset_type":"scripted_synthetic_matches",
        "seed_count":len(seeds),
        "cases":scenarios,
        "totals":{
            "simulated_events":sum(s["events"] for s in scenarios),
            "validated_broadcast_cues":sum(s["broadcast_cues"] for s in scenarios),
            "verified_persona_stories":story_count,
            "adversarial_recovery_cases":3,
            "failures":0,
        },
        "recovery":recovery,
        "model_validation":{
            "foundry_local_available_in_ci":False,
            "real_phi_inference_exercised":False,
            "note":"Use python -m scripts.probe_foundry_local with an actual local server for inference validation.",
        },
        "elapsed_seconds":round(time.perf_counter()-started,3),
    }


def markdown(report: dict) -> str:
    totals=report["totals"]
    rows="\n".join(
        f"| {c['seed']} | {c['events']} | {c['possessions']} | {c['insights']} | "
        f"{c['tactical_shift_insights']} | {c['verified_persona_stories']} |"
        for c in report["cases"]
    )
    return f"""# MatchShift AI — Automated evaluation

**Evaluation mode:** deterministic Microsoft Agent Framework workflow over **scripted synthetic** matches.
**No real Phi inference was exercised.** These are integrity and reliability tests, **not**
accuracy scores for professional football analysis or empirical hallucination rates.

| Seed | Events | Possessions | Insights | Shift alerts | Verified persona stories |
| --- | ---: | ---: | ---: | ---: | ---: |
{rows}

## Test totals

- Evaluated match scenarios: **{report['seed_count']}**
- Synthetic match events: **{totals['simulated_events']}**
- Grounded broadcast cues: **{totals['validated_broadcast_cues']}**
- Verified end-to-end agent story executions: **{totals['verified_persona_stories']}**
- Adversarial recovery cases: **3** (invalid angle, invalid style, unavailable provider)
- Evaluation failures: **{totals['failures']}**

Every story completed the Tactical Analyst → Narrative Director → Evidence Verifier →
Audience Agent workflow with source event IDs unchanged. Numeric shift claims and
broadcast timings were recomputed from synthetic event data.

## Limits and scope

The matches include deliberately scripted goals and a pressing-related recovery
sequence. Passing the evaluation does not establish football realism, external
generalization, model accuracy, or successful Foundry Local inference.
For real local model smoke testing see `docs/foundry-local-validation.md`.

Generated by `python -m scripts.evaluate`. Do not edit numeric results by hand.
"""


def main() -> None:
    parser=argparse.ArgumentParser(description="Evaluate synthetic match integrity and Microsoft Agent Framework recovery")
    parser.add_argument("--seeds",default=",".join(str(s) for s in DEFAULT_SEEDS),
                        help="Unique comma-separated integer seeds")
    parser.add_argument("--out",type=Path,default=Path("artifacts/evaluation"))
    args=parser.parse_args()
    try:
        seeds=tuple(int(x.strip()) for x in args.seeds.split(","))
    except ValueError:
        parser.error("All seeds must be integers")
    report=asyncio.run(evaluate(seeds))
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"evaluation.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    (args.out/"evaluation.md").write_text(markdown(report),encoding="utf-8")
    print(markdown(report),flush=True)


if __name__=="__main__":
    main()
