"""No AI claims: event-count metrics and possession boundaries are fully reproducible."""
from packages.simulator.models import (
    MatchEvent, MetricSnapshot, PossessionSummary, TeamMetrics,
)

WINDOW = 300  # 5 minutes

def build_possessions(events: list[MatchEvent]) -> list[PossessionSummary]:
    if not events:
        return []
    chains: list[PossessionSummary] = []
    current: list[MatchEvent] = []
    for event in events:
        if current and event.possession_id != current[-1].possession_id:
            chains.append(_summary(current, "dispossessed"))
            current = []
        current.append(event)
    if current:
        chains.append(_summary(current, "replay_end"))
    return chains

def _summary(events: list[MatchEvent], fallback: str) -> PossessionSummary:
    last = events[-1]
    end_reason = (
        "goal" if last.kind == "goal" else
        "shot" if last.kind == "shot" else
        "pass_lost" if last.kind == "pass" and not last.success else fallback
    )
    return PossessionSummary(
        id=events[0].possession_id, team=events[0].team,
        start_second=events[0].second, end_second=last.second,
        event_ids=[event.id for event in events], end_reason=end_reason,
    )

def _team_metrics(events: list[MatchEvent], team: str) -> TeamMetrics:
    owned = [e for e in events if e.team == team]
    passes = [e for e in owned if e.kind == "pass"]
    completed = sum(e.success for e in passes)
    regains = [e for e in owned if e.kind in ("turnover", "tackle")]
    high_regains = sum(
        (e.position.x >= 60 if team == "home" else e.position.x <= 40)
        for e in regains
    )
    return TeamMetrics(
        actions=len(owned), regains=len(regains), high_regains=high_regains,
        pass_attempts=len(passes), pass_completed=completed,
        pass_accuracy_pct=round(100 * completed / len(passes), 1) if passes else None,
        shots=sum(e.kind in ("goal", "shot") for e in owned),
        goals=sum(e.kind == "goal" for e in owned),
    )

def snapshot_at(events: list[MatchEvent], second: int, window: int = WINDOW) -> MetricSnapshot:
    if second < 0 or window <= 0:
        raise ValueError("second must be >= 0 and window must be > 0")
    recent = [event for event in events if second - window < event.second <= second]
    return MetricSnapshot(
        second=second, window_seconds=window,
        home=_team_metrics(recent, "home"),
        away=_team_metrics(recent, "away"),
    )

def rolling_snapshots(events: list[MatchEvent], duration: int) -> list[MetricSnapshot]:
    return [snapshot_at(events, second) for second in range(60, duration + 1, 60)]
