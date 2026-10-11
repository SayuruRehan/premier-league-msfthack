"""The public, documented contract shared by the simulator, analytics and API."""
from typing import Literal
from pydantic import BaseModel, Field

Team = Literal["home", "away"]
EventKind = Literal["pass", "turnover", "shot", "goal", "tackle"]

class Position(BaseModel):
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)

class MatchEvent(BaseModel):
    id: str
    second: int = Field(ge=0, le=5400)
    team: Team
    kind: EventKind
    player: str
    position: Position
    target: Position | None = None
    success: bool = True
    description: str
    possession_id: str

class TeamMetrics(BaseModel):
    actions: int = Field(ge=0)
    regains: int = Field(ge=0)
    high_regains: int = Field(ge=0)
    pass_attempts: int = Field(ge=0)
    pass_completed: int = Field(ge=0)
    pass_accuracy_pct: float | None = Field(default=None, ge=0, le=100)
    shots: int = Field(ge=0)
    goals: int = Field(ge=0)

class MetricSnapshot(BaseModel):
    second: int
    window_seconds: int = 300
    home: TeamMetrics
    away: TeamMetrics

class PossessionSummary(BaseModel):
    id: str
    team: Team
    start_second: int
    end_second: int
    event_ids: list[str]
    end_reason: Literal["pass_lost", "shot", "goal", "dispossessed", "replay_end"]

class EvidenceInsight(BaseModel):
    id: str
    second: int
    title: str
    explanation: str
    evidence_event_ids: list[str]
    metric_name: str
    metric_value: float
    kind: Literal["goal", "tactical_shift"] = "goal"
    team: Team | None = None
    comparison_value: float | None = None

class BroadcastCue(BaseModel):
    """Time-bound, traceable on-screen direction from trusted synthetic insights."""
    id: str
    insight_id: str
    second: int = Field(ge=0, le=5400)
    until_second: int = Field(ge=0, le=5400)
    kind: Literal["goal", "tactical_shift"]
    team: Team
    headline: str
    subtitle: str
    metric_label: str
    metric_value: float
    focus: Position
    evidence_event_ids: list[str]

class MatchReplay(BaseModel):
    match_id: str
    synthetic: bool = True
    duration_seconds: int
    home_name: str
    away_name: str
    home_score: int
    away_score: int
    events: list[MatchEvent]
    possessions: list[PossessionSummary]
    snapshots: list[MetricSnapshot]
    insights: list[EvidenceInsight]
    cues: list[BroadcastCue]
