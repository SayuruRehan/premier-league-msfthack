from fastapi.testclient import TestClient
from services.api.app.main import app
from packages.simulator.generator import GOALS, generate_events
from packages.analytics.insights import generate_insights
from packages.analytics.metrics import build_possessions, snapshot_at, rolling_snapshots

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
    assert len(data["snapshots"]) == 90
    assert data["events"] == sorted(data["events"], key=lambda e: e["second"])
    assert all(0 <= e["position"][axis] <= 100 for e in data["events"] for axis in ("x", "y"))
    assert all(e["possession_id"].startswith("pos-") for e in data["events"])

def test_event_possession_consistency():
    for seed in (0, 7, 12, 42, 100):
        events = generate_events(seed)
        assert [(e.second, e.team) for e in events if e.kind == "goal"] == list(GOALS.items())
        for previous, event in zip(events, events[1:]):
            if previous.possession_id == event.possession_id:
                assert previous.team == event.team
                assert previous.kind not in ("goal", "shot")
                assert previous.success
                assert event.kind not in ("turnover", "tackle")
            if event.kind in ("turnover", "tackle"):
                assert event.team != previous.team
        chains = build_possessions(events)
        assert [eid for chain in chains for eid in chain.event_ids] == [e.id for e in events]
        assert len({chain.id for chain in chains}) == len(chains)
        assert all(chain.start_second <= chain.end_second for chain in chains)

def test_metrics_no_future_leakage_and_denominators():
    events = generate_events()
    for now in (120, 300, 600, 4200):
        early = [event for event in events if event.second <= now]
        assert snapshot_at(events, now) == snapshot_at(early, now)
        snap = snapshot_at(events, now)
        for team in (snap.home, snap.away):
            assert team.high_regains <= team.regains <= team.actions
            assert team.pass_completed <= team.pass_attempts
            assert team.pass_accuracy_pct is None if team.pass_attempts == 0 else team.pass_accuracy_pct is not None
    assert len(rolling_snapshots(events, 5400)) == 90

def test_tactical_shift_is_measurable():
    events = generate_events(7)
    insights = generate_insights(events)
    shifts = [insight for insight in insights if insight.kind == "tactical_shift" and insight.team == "away"]
    assert shifts, "synthetic scripted pressure phase should trigger a measurable shift"
    first = shifts[0]
    assert 67 * 60 <= first.second <= 74 * 60
    now = snapshot_at(events, first.second).away
    before = snapshot_at(events, first.second - 300).away
    assert first.metric_value == now.high_regains - before.high_regains
    assert first.comparison_value == before.high_regains

def test_all_insights_have_verifiable_evidence():
    events = generate_events()
    lookup = {e.id: e for e in events}
    for insight in generate_insights(events):
        assert insight.evidence_event_ids
        assert len(insight.evidence_event_ids) == len(set(insight.evidence_event_ids))
        assert all(eid in lookup and lookup[eid].second <= insight.second for eid in insight.evidence_event_ids)
        if insight.kind == "goal":
            goal = lookup[insight.evidence_event_ids[-1]]
            assert goal.kind == "goal"
            assert insight.metric_value == sum(e.team == goal.team for e in events if goal.second - 300 < e.second < goal.second)
        else:
            now = snapshot_at(events, insight.second)
            before = snapshot_at(events, insight.second - 300)
            assert insight.metric_value == getattr(now, insight.team).high_regains - getattr(before, insight.team).high_regains
            assert {e.id for e in events if insight.second - 600 < e.second <= insight.second} == set(insight.evidence_event_ids)

def test_bad_seed():
    assert client.get("/api/matches/demo?seed=-1").status_code == 422
