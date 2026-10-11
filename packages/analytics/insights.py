"""Evidence-verified, conservative interpretations of synthetic events.

The "high press" signal is explicitly a *proxy based on regains by location*.
It is not measured defensive pressure, tracking-derived PPDA or causation.
"""
from packages.simulator.models import MatchEvent, EvidenceInsight
from .metrics import WINDOW, snapshot_at

def generate_insights(events: list[MatchEvent]) -> list[EvidenceInsight]:
    if not events:
        return []
    results: list[EvidenceInsight] = []
    for event in events:
        if event.kind != "goal":
            continue
        window = [e for e in events if event.second - WINDOW < e.second < event.second]
        recent = [e for e in window if e.team == event.team]
        title = "Northbridge strike first" if event.team == "home" else "Harbor City change the score"
        results.append(EvidenceInsight(
            id=f"insight-{event.id}", second=event.second, title=title,
            explanation=f"A goal follows {len(recent)} attacking-team actions in the preceding five minutes. This is a count of synthetic actions, not a causal claim.",
            evidence_event_ids=[e.id for e in recent] + [event.id],
            metric_name="team_actions_previous_5min", metric_value=float(len(recent)),
            kind="goal", team=event.team,
        ))
    # Compare non-overlapping five-minute windows; require three additional
    # high regains. A ten-minute cooldown avoids repetitive notifications.
    last_shift: dict[str, int] = {"home": -10000, "away": -10000}
    final_second = events[-1].second
    for second in range(WINDOW * 2, final_second + 1, 60):
        now = snapshot_at(events, second)
        before = snapshot_at(events, second - WINDOW)
        for team in ("home", "away"):
            recent = getattr(now, team)
            previous = getattr(before, team)
            delta = recent.high_regains - previous.high_regains
            if recent.high_regains < 3 or delta < 3 or second - last_shift[team] < 600:
                continue
            label = "Northbridge" if team == "home" else "Harbor City"
            evidence = [e.id for e in events if second - WINDOW * 2 < e.second <= second]
            results.append(EvidenceInsight(
                id=f"shift-{team}-{second}", second=second,
                title=f"{label} high-regain surge",
                explanation=f"{label} recorded {recent.high_regains} regains in the attacking-zone proxy in five minutes, versus {previous.high_regains} in the preceding five. This indicates a shift in our simulated ball-winning pattern, not independently measured pressing intensity.",
                evidence_event_ids=evidence,
                metric_name="high_regains_5min_delta", metric_value=float(delta),
                kind="tactical_shift", team=team, comparison_value=float(previous.high_regains),
            ))
            last_shift[team] = second
    return sorted(results, key=lambda insight: (insight.second, insight.id))
