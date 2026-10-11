from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from packages.analytics.insights import generate_insights
from packages.analytics.metrics import build_possessions, rolling_snapshots
from packages.analytics.broadcast import build_cues
from packages.simulator.generator import DURATION, HOME, AWAY, generate_events
from packages.simulator.models import MatchReplay

from packages.agents.contracts import Audience, StoryRequest, StoryResponse
from packages.agents.workflow import inference_mode, run_story

app = FastAPI(title="MatchShift AI API", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/matches/demo", response_model=MatchReplay)
def demo(seed: int = Query(default=7, ge=0, le=1000000)):
    events = generate_events(seed)
    insights = generate_insights(events)
    return MatchReplay(
        match_id=f"synthetic-{seed}", duration_seconds=DURATION,
        home_name=HOME[0], away_name=AWAY[0],
        home_score=sum(e.team == "home" and e.kind == "goal" for e in events),
        away_score=sum(e.team == "away" and e.kind == "goal" for e in events),
        events=events, possessions=build_possessions(events),
        snapshots=rolling_snapshots(events, DURATION), insights=insights,
        cues=build_cues(events, insights, DURATION),
    )

@app.get("/api/agents/config")
def agent_config():
    return {"framework": "Microsoft Agent Framework", "workflow": "MatchShiftStoryPipeline",
            "inference_mode": inference_mode(), "local_only": True}

@app.get("/api/matches/demo/story", response_model=StoryResponse)
async def match_story(
    seed: int = Query(default=7, ge=0, le=1000000),
    insight_id: str = Query(min_length=1, max_length=100),
    audience: Audience = "fan",
):
    available = {i.id for i in generate_insights(generate_events(seed))}
    if insight_id not in available:
        raise HTTPException(status_code=404, detail="Insight not found for this synthetic match")
    return await run_story(StoryRequest(seed=seed, insight_id=insight_id, audience=audience))
