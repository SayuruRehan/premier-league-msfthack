"""Opt-in *real* Foundry Local smoke test for the two model-backed agent roles.

No mocked responses or deterministic-only story can pass. Do not run in CI
unless a real local model runtime has been provisioned.
"""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path

from packages.agents.contracts import StoryRequest
from packages.agents.workflow import run_story
from packages.analytics.insights import generate_insights
from packages.simulator.generator import generate_events


async def probe(seed: int, audience: str) -> dict:
    if os.getenv("MATCHSHIFT_INFERENCE","").lower()!="foundry_local":
        raise RuntimeError("Set MATCHSHIFT_INFERENCE=foundry_local before running the real model probe")
    insight=next((i for i in generate_insights(generate_events(seed)) if i.kind=="goal"),None)
    if insight is None:
        raise RuntimeError("No synthetic goal insight available")
    started=time.perf_counter()
    result=await run_story(StoryRequest(seed=seed,insight_id=insight.id,audience=audience))
    elapsed=round(time.perf_counter()-started,3)
    # Fail closed: the fallback route is healthy, but not proof of AI integration.
    if result.source!="foundry_local" or result.style_source!="foundry_local":
        raise RuntimeError(
            "Local Phi model was NOT proven: one or both decisions used fallback. "
            f"Director={result.source}, AudienceStyle={result.style_source}. "
            "Verify Foundry Local's served URL, actual model ID and chat completions API."
        )
    if not result.verified or not result.evidence_event_ids or any(
        step.status=="rejected" for step in result.trace
    ):
        raise RuntimeError("Model output failed evidence verification")
    return {
        "probe_type":"real_foundry_local",
        "result":"passed",
        "seed":seed,"audience":audience,"insight_id":insight.id,
        "director_source":result.source,
        "style_source":result.style_source,
        "presentation_style":result.presentation_style,
        "narrative_angle":result.angle,
        "agent_stages":[step.stage for step in result.trace],
        "model_id":os.getenv("MATCHSHIFT_LOCAL_MODEL","phi-4-mini"),
        "endpoint_host":"localhost",
        "elapsed_seconds":elapsed,
        "verified":result.verified,
        "evidence_ids":result.evidence_event_ids,
    }


def main() -> None:
    parser=argparse.ArgumentParser(description="Require a real local Phi inference success for both agent decisions")
    parser.add_argument("--seed",type=int,default=7)
    parser.add_argument("--audience",choices=("fan","analyst","broadcast"),default="broadcast")
    parser.add_argument("--out",type=Path,default=Path("artifacts/foundry-local-probe.json"))
    args=parser.parse_args()
    if not (0<=args.seed<=1_000_000):
        parser.error("Seed must be between 0 and 1,000,000")
    report=asyncio.run(probe(args.seed,args.audience))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PASS: Actual Foundry Local decisions were validated by the Agent Framework workflow.")
    print(f"Model: {report['model_id']}; elapsed: {report['elapsed_seconds']}s; evidence events: {len(report['evidence_ids'])}")


if __name__=="__main__":
    main()
