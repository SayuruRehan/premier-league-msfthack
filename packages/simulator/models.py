from typing import Literal
from pydantic import BaseModel, Field

EventKind = Literal["pass", "turnover", "shot", "goal", "tackle"]

class Position(BaseModel):
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)

class MatchEvent(BaseModel):
    id: str
    second: int = Field(ge=0, le=5400)
    team: Literal["home", "away"]
    kind: EventKind
    player: str
    position: Position
    target: Position | None = None
    success: bool = True
    description: str

class EvidenceInsight(BaseModel):
    id: str
    second: int
    title: str
    explanation: str
    evidence_event_ids: list[str]
    metric_name: str
    metric_value: float

class MatchReplay(BaseModel):
    match_id: str
    synthetic: bool = True
    duration_seconds: int
    home_name: str
    away_name: str
    home_score: int
    away_score: int
    events: list[MatchEvent]
    insights: list[EvidenceInsight]
