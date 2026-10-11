from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from packages.analytics.insights import generate_insights
from packages.analytics.metrics import build_possessions, rolling_snapshots
from packages.simulator.generator import DURATION, HOME, AWAY, generate_events
from packages.simulator.models import MatchReplay

app = FastAPI(title="MatchShift AI API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/matches/demo", response_model=MatchReplay)
def demo(seed: int = Query(default=7, ge=0, le=1000000)):
    events = generate_events(seed)
    return MatchReplay(
        match_id=f"synthetic-{seed}", duration_seconds=DURATION,
        home_name=HOME[0], away_name=AWAY[0],
        home_score=sum(e.team == "home" and e.kind == "goal" for e in events),
        away_score=sum(e.team == "away" and e.kind == "goal" for e in events),
        events=events, possessions=build_possessions(events),
        snapshots=rolling_snapshots(events, DURATION), insights=generate_insights(events),
    )
