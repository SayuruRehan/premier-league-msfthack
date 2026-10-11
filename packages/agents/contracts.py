"""Stable API contracts for audited agent handoffs."""
from typing import Literal
from pydantic import BaseModel, Field

Audience = Literal["fan", "analyst", "broadcast"]
Source = Literal["deterministic", "foundry_local", "fallback"]

class StoryRequest(BaseModel):
    seed: int = Field(ge=0, le=1_000_000)
    insight_id: str
    audience: Audience = "fan"

class Analysis(BaseModel):
    seed: int
    insight_id: str
    second: int
    kind: Literal["goal", "tactical_shift"]
    team: Literal["home", "away"]
    title: str
    explanation: str
    metric_name: str
    metric_value: float
    comparison_value: float | None = None
    evidence_event_ids: list[str]

class DirectorDecision(BaseModel):
    analysis: Analysis
    angle: str
    source: Source
    note: str

class Verification(BaseModel):
    decision: DirectorDecision
    approved: bool
    reason: str

class StageTrace(BaseModel):
    stage: str
    status: Literal["completed", "approved", "rejected", "fallback"]
    detail: str
    evidence_event_ids: list[str] = Field(default_factory=list)

class StoryResponse(BaseModel):
    insight_id: str
    audience: Audience
    headline: str
    narration: str
    angle: str
    verified: bool
    source: Source
    evidence_event_ids: list[str]
    framework: str = "Microsoft Agent Framework"
    trace: list[StageTrace]
