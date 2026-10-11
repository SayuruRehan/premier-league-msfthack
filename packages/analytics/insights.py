"""Deterministic insights grounded in event IDs; a future input to AI agents."""
from packages.simulator.models import MatchEvent, EvidenceInsight

def generate_insights(events: list[MatchEvent]) -> list[EvidenceInsight]:
    results: list[EvidenceInsight] = []
    for event in events:
        if event.kind != "goal":
            continue
        window = [e for e in events if event.second - 300 <= e.second < event.second]
        recent = [e for e in window if e.team == event.team]
        title = "Northbridge strike first" if event.team == "home" else "Harbor City change the match"
        results.append(EvidenceInsight(
            id=f"insight-{event.id}", second=event.second, title=title,
            explanation=f"A goal follows {len(recent)} attacking-team actions in the preceding five minutes. This is a count of simulated events, not a causal claim.",
            evidence_event_ids=[e.id for e in recent] + [event.id],
            metric_name="team_actions_previous_5min", metric_value=float(len(recent)),
        ))
    return results
