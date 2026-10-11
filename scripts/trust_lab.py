"""Generate judge-visible *simulated failure tests* through the REAL Agent Framework workflow.

Important: these scenarios replace model response functions with controlled test
stubs. There is NO live Phi inference. The workflow orchestration, evidence
verifier, rejection trace and fallback paths do execute normally.
"""
import os
from unittest.mock import patch

from packages.agents.contracts import StoryRequest
from packages.agents.workflow import run_story
from packages.analytics.insights import generate_insights
from packages.simulator.generator import generate_events

CASES = ("fabricated_claim", "provider_outage", "invalid_style")
BAD_ANGLE = "invented_200_goals_and_red_cards"
BAD_STYLE = "invent_a_secret_match_fixing_claim"


async def build_trust_lab(seed: int = 7) -> dict:
    goal = next((item for item in generate_insights(generate_events(seed))
                 if item.kind == "goal"), None)
    if goal is None:
        raise ValueError("Cannot demonstrate rejection without an actual goal insight")
    request = StoryRequest(seed=seed, insight_id=goal.id, audience="broadcast")

    async def fabricated_claim(_analysis):
        return BAD_ANGLE

    async def offline(_analysis):
        raise ConnectionError("Simulated inference provider unavailable")

    async def permitted(_analysis):
        return "scoreline"

    async def malformed_style(_analysis, _audience):
        return BAD_STYLE

    # These replace only provider decisions. The @workflow and @step functions
    # still execute through Microsoft Agent Framework; no external calls occur.
    import packages.agents.workflow as agent_module

    with patch.dict(os.environ, {"MATCHSHIFT_INFERENCE": "foundry_local"}):
        with patch.object(agent_module, "choose_with_foundry_local", fabricated_claim):
            injected = await run_story(request)
        with patch.object(agent_module, "choose_with_foundry_local", offline):
            unavailable = await run_story(request)
        with patch.object(agent_module, "choose_with_foundry_local", permitted), \
             patch.object(agent_module, "choose_style_with_foundry_local", malformed_style):
            invalid_style = await run_story(request)

    cases = {
        "fabricated_claim": {
            "label": "Invented match claim",
            "question": "What happens if a director suggests something the data cannot support?",
            "simulated_provider_output": BAD_ANGLE,
            "expected_behavior": "Verifier rejects the angle and a safe retry succeeds.",
            "story": injected.model_dump(mode="json"),
        },
        "provider_outage": {
            "label": "Model endpoint unavailable",
            "question": "Does the broadcast break if the local model stops answering?",
            "simulated_provider_output": "[Simulated ConnectionError]",
            "expected_behavior": "Director uses a labeled deterministic fallback.",
            "story": unavailable.model_dump(mode="json"),
        },
        "invalid_style": {
            "label": "Unapproved audience style",
            "question": "Can the audience agent introduce unsupported allegations?",
            "simulated_provider_output": BAD_STYLE,
            "expected_behavior": "Audience stage rejects unsupported style and renders a trusted template.",
            "story": invalid_style.model_dump(mode="json"),
        },
    }
    lab = {
        "version": 1,
        "synthetic": True,
        "simulated_failure_tests": True,
        "live_model_inference": False,
        "execution": "Real Microsoft Agent Framework orchestration with controlled model-response test stubs",
        "seed": seed,
        "insight_id": goal.id,
        "cases": cases,
    }
    validate_trust_lab(lab, {i.id: i for i in generate_insights(generate_events(seed))})
    return lab


def validate_trust_lab(lab: dict, insights: dict) -> None:
    if lab.get("live_model_inference") is not False or lab.get("simulated_failure_tests") is not True:
        raise ValueError("Failure demonstrations must be identified as simulated, not real Phi inference")
    if set(lab.get("cases", {})) != set(CASES):
        raise ValueError("Missing a trust lab failure case")
    insight = insights.get(lab["insight_id"])
    if insight is None:
        raise ValueError("Trust lab insight does not appear in synthetic replay")

    for case_id in CASES:
        case = lab["cases"][case_id]
        story = case["story"]
        if story["insight_id"] != insight.id or story["audience"] != "broadcast":
            raise ValueError("Trust lab result is not the selected broadcast insight")
        if story["verified"] is not True or story["evidence_event_ids"] != insight.evidence_event_ids:
            raise ValueError("An unverified or tampered story appeared in the trust lab")
        if insight.explanation not in story["narration"]:
            raise ValueError("The verified source observation is missing")
        if case["simulated_provider_output"] in story["narration"] or case["simulated_provider_output"] in story["headline"]:
            raise ValueError("Untrusted model proposal was published")
        trace = story.get("trace", [])
        stages = [step["stage"] for step in trace]
        if not {"TacticalAnalyst", "NarrativeDirector", "EvidenceVerifier", "AudienceAgent"}.issubset(stages):
            raise ValueError("Trust lab skipped an Agent Framework stage")
        if trace[-1]["stage"] != "AudienceAgent":
            raise ValueError("Trust lab did not complete audience rendering")
        if case_id == "fabricated_claim":
            if story["source"] != "fallback" or not any(t["status"] == "rejected" for t in trace):
                raise ValueError("Injected claim did not cause verifier rejection and recovery")
            if stages.count("EvidenceVerifier") != 2:
                raise ValueError("Injected claim recovery did not re-run the verifier")
        elif case_id == "provider_outage":
            if story["source"] != "fallback" or not any(t["status"] == "fallback" for t in trace):
                raise ValueError("Outage did not lead to transparent fallback")
        elif case_id == "invalid_style":
            # "foundry_local" is the simulated accepted director token here, not a real model call.
            if story["style_source"] != "fallback":
                raise ValueError("Unapproved style did not fall back to safe narration")
            if trace[-1]["status"] != "fallback":
                raise ValueError("Audience agent did not mark recovery in its trace")
