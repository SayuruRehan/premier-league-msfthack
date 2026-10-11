from fastapi.testclient import TestClient
from services.api.app.main import app
from packages.simulator.generator import generate_events
from packages.analytics.insights import generate_insights

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_determinism_and_seed_variation():
    assert generate_events(7) == generate_events(7)
    assert generate_events(7) != generate_events(8)

def test_replay_contract_and_score():
    response = client.get("/api/matches/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["synthetic"] is True
    assert (data["home_score"], data["away_score"]) == (1, 2)
    assert len(data["events"]) == 180
    assert data["events"] == sorted(data["events"], key=lambda e: e["second"])
    assert all(0 <= e["position"][axis] <= 100 for e in data["events"] for axis in ("x", "y"))

def test_insight_evidence_and_no_future_leakage():
    events = generate_events()
    lookup = {e.id: e for e in events}
    for insight in generate_insights(events):
        assert insight.evidence_event_ids
        assert all(eid in lookup for eid in insight.evidence_event_ids)
        assert all(lookup[eid].second <= insight.second for eid in insight.evidence_event_ids)
        goal = lookup[insight.evidence_event_ids[-1]]
        assert goal.kind == "goal"
        assert insight.metric_value == sum(e.team == goal.team for e in events if goal.second - 300 <= e.second < goal.second)

def test_bad_seed():
    assert client.get("/api/matches/demo?seed=-1").status_code == 422
