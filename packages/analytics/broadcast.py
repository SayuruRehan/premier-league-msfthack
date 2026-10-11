"""Deterministic, evidence-backed broadcast cue sheet.

This is scheduled replay direction — not inferred video tracking or live footage.
Every cue begins exactly when its source insight becomes available.
"""
from packages.simulator.models import BroadcastCue, EvidenceInsight, MatchEvent

CUE_SECONDS = 180

def build_cues(
    events: list[MatchEvent],
    insights: list[EvidenceInsight],
    duration_seconds: int,
) -> list[BroadcastCue]:
    by_id = {event.id: event for event in events}
    cues: list[BroadcastCue] = []
    for insight in sorted(insights, key=lambda item: (item.second, item.id)):
        if not insight.evidence_event_ids or insight.team is None:
            continue
        evidence = [by_id[event_id] for event_id in insight.evidence_event_ids]
        if any(event.second > insight.second for event in evidence):
            raise ValueError("Broadcast cues may not reference future events")
        # Tactical cues focus on an actual regain where possible; goals focus on the goal.
        if insight.kind == "goal":
            focus_event = next(
                (event for event in reversed(evidence)
                 if event.kind == "goal" and event.team == insight.team), evidence[-1]
            )
            label = "ATTACKING ACTIONS · PREVIOUS 5 MIN"
        else:
            focus_event = next(
                (event for event in reversed(evidence)
                 if event.team == insight.team and event.kind in ("turnover", "tackle")), evidence[-1]
            )
            label = "HIGH-REGAIN CHANGE · 5 MIN"
        cues.append(BroadcastCue(
            id=f"cue-{insight.id}", insight_id=insight.id, second=insight.second,
            until_second=min(duration_seconds, insight.second + CUE_SECONDS),
            kind=insight.kind, team=insight.team, headline=insight.title,
            subtitle=insight.explanation, metric_label=label,
            metric_value=insight.metric_value, focus=focus_event.position,
            evidence_event_ids=insight.evidence_event_ids,
        ))
    return cues
