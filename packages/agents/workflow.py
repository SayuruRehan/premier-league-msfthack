"""Microsoft Agent Framework orchestration for safe, explainable football stories.

Each role is a separate @step with an explicit typed handoff. In zero-cost mode,
all roles are deterministic. If the operator opts in to Foundry Local, an actual
Agent chooses the narrative *angle*; all displayed claims still come from a
separately verified evidence pack. Invalid model choices are rejected and the
workflow retries once with a safe deterministic decision. No cloud calls occur.
"""
import asyncio
import os
from urllib.parse import urlparse

from agent_framework import workflow, step
from packages.analytics.insights import generate_insights
from packages.simulator.generator import generate_events
from .contracts import (
    Analysis, DirectorDecision, StageTrace, StoryRequest, StoryResponse, Verification,
)

ANGLES = {"scoreline", "momentum", "evidence"}
PREFERRED = {"goal": "scoreline", "tactical_shift": "momentum"}


def inference_mode() -> str:
    return "foundry_local" if os.getenv("MATCHSHIFT_INFERENCE", "deterministic").lower() == "foundry_local" else "deterministic"


@step(name="TacticalAnalyst")
async def tactical_analyst(request: StoryRequest) -> Analysis:
    events = generate_events(request.seed)
    insight = next((item for item in generate_insights(events) if item.id == request.insight_id), None)
    if insight is None or insight.team is None:
        raise ValueError("Unknown insight for the chosen synthetic match")
    return Analysis(
        seed=request.seed, insight_id=insight.id, second=insight.second,
        kind=insight.kind, team=insight.team, title=insight.title,
        explanation=insight.explanation, metric_name=insight.metric_name,
        metric_value=insight.metric_value, comparison_value=insight.comparison_value,
        evidence_event_ids=insight.evidence_event_ids,
    )


async def choose_with_foundry_local(analysis: Analysis) -> str:
    """Actual Agent Framework agent over Foundry Local's chat-completions API."""
    from agent_framework import Agent
    from agent_framework.openai import OpenAIChatCompletionClient

    url = os.getenv("MATCHSHIFT_LOCAL_URL", "http://127.0.0.1:5273/v1/")
    if urlparse(url).scheme != "http" or urlparse(url).hostname not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("MATCHSHIFT_LOCAL_URL must be a local HTTP endpoint")
    client = OpenAIChatCompletionClient(
        base_url=url, api_key="local",
        model=os.getenv("MATCHSHIFT_LOCAL_MODEL", "phi-4-mini"),
    )
    agent = Agent(
        client=client,
        name="NarrativeDirector",
        instructions=(
            "You direct a fictional football match broadcast. Choose exactly ONE token "
            "from: scoreline, momentum, evidence. Respond with that token only. "
            "Do not introduce or invent football statistics or details."
        ),
    )
    prompt = (
        f"Event type: {analysis.kind}. Title: {analysis.title}. "
        f"Confirmed observation: {analysis.explanation}. "
        "Pick the clearest storytelling angle. Return exactly one token."
    )
    response = await asyncio.wait_for(agent.run(prompt), timeout=12)
    return response.text.strip().strip("\x60").lower()


@step(name="NarrativeDirector")
async def narrative_director(analysis: Analysis) -> DirectorDecision:
    if inference_mode() == "deterministic":
        return DirectorDecision(analysis=analysis, angle=PREFERRED[analysis.kind],
                                source="deterministic", note="Local free-mode angle selection")
    try:
        selected = await choose_with_foundry_local(analysis)
        return DirectorDecision(analysis=analysis, angle=selected,
                                source="foundry_local", note="Angle proposed by local Phi model")
    except Exception:
        # Not a silent fabricated AI success: the provenance clearly says fallback.
        return DirectorDecision(analysis=analysis, angle=PREFERRED[analysis.kind],
                                source="fallback", note="Local inference unavailable; safe fallback")


@step(name="EvidenceVerifier")
async def evidence_verifier(decision: DirectorDecision) -> Verification:
    analysis = decision.analysis
    expected = next(
        (i for i in generate_insights(generate_events(analysis.seed)) if i.id == analysis.insight_id),
        None,
    )
    if expected is None:
        return Verification(decision=decision, approved=False, reason="Insight missing from source replay")
    if decision.angle not in ANGLES:
        return Verification(decision=decision, approved=False, reason="Unapproved narrative angle")
    if (analysis.second != expected.second or analysis.title != expected.title
        or analysis.explanation != expected.explanation
        or analysis.metric_name != expected.metric_name
        or analysis.metric_value != expected.metric_value
        or analysis.comparison_value != expected.comparison_value
        or analysis.team != expected.team or analysis.kind != expected.kind
        or analysis.evidence_event_ids != expected.evidence_event_ids):
        return Verification(decision=decision, approved=False,
                            reason="A claim or evidence ID did not match source data")
    return Verification(decision=decision, approved=True, reason="Claims, timestamps and event IDs revalidated")


@step(name="AudienceAgent")
async def audience_agent(verification: Verification, audience: str) -> StoryResponse:
    if not verification.approved:
        raise ValueError("Refusing to broadcast an unverified insight")
    a = verification.decision.analysis
    angle = verification.decision.angle
    if audience == "fan":
        headline = f"{a.title}!"
        narration = f"Here's the turning point: {a.explanation}"
    elif audience == "analyst":
        headline = f"Tactical evidence · {a.title}"
        narration = f"Signal: {a.metric_name} = {a.metric_value:g}. {a.explanation}"
    elif audience == "broadcast":
        headline = a.title.upper()
        narration = a.explanation
    else:
        raise ValueError("Unsupported audience")
    return StoryResponse(
        insight_id=a.insight_id, audience=audience, headline=headline,
        narration=narration, angle=angle, verified=True,
        source=verification.decision.source, evidence_event_ids=a.evidence_event_ids,
        trace=[],
    )


@workflow(name="MatchShiftStoryPipeline")
async def story_pipeline(request: StoryRequest) -> StoryResponse:
    analysis = await tactical_analyst(request)
    trace = [StageTrace(stage="TacticalAnalyst", status="completed",
                        detail="Read the match and assembled an evidence-linked observation",
                        evidence_event_ids=analysis.evidence_event_ids)]

    decision = await narrative_director(analysis)
    trace.append(StageTrace(stage="NarrativeDirector",
                            status="fallback" if decision.source == "fallback" else "completed",
                            detail=decision.note))

    verification = await evidence_verifier(decision)
    trace.append(StageTrace(stage="EvidenceVerifier",
                            status="approved" if verification.approved else "rejected",
                            detail=verification.reason,
                            evidence_event_ids=analysis.evidence_event_ids))
    if not verification.approved:
        # Bounded recovery: reject invented angles and ask for a known safe option.
        recovered = DirectorDecision(
            analysis=analysis, angle=PREFERRED[analysis.kind], source="fallback",
            note="Rejected director output; restored known-safe angle",
        )
        trace.append(StageTrace(stage="NarrativeDirector", status="fallback", detail=recovered.note))
        verification = await evidence_verifier(recovered)
        trace.append(StageTrace(stage="EvidenceVerifier",
                                status="approved" if verification.approved else "rejected",
                                detail=verification.reason))
        if not verification.approved:
            raise ValueError("Safe fallback could not be verified")

    result = await audience_agent(verification, request.audience)
    trace.append(StageTrace(stage="AudienceAgent", status="completed",
                            detail=f"Rendered verified {request.audience} narration"))
    return result.model_copy(update={"trace": trace})


async def run_story(request: StoryRequest) -> StoryResponse:
    # Build per request: do not share mutable workflow run state across users.
    pipeline = story_pipeline.build()
    completed = await pipeline.run(request)
    outputs = completed.get_outputs()
    if len(outputs) != 1 or not isinstance(outputs[0], StoryResponse):
        raise RuntimeError("The Microsoft Agent Framework workflow did not return a story")
    return outputs[0]
