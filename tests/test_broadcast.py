"""Broadcast direction must be temporally accurate and evidence-linked."""
from packages.simulator.generator import DURATION, generate_events
from packages.analytics.insights import generate_insights
from packages.analytics.broadcast import build_cues
from fastapi.testclient import TestClient
from services.api.app.main import app

client = TestClient(app)

def test_cues_are_complete_and_ordered():
    events = generate_events()
    insights = generate_insights(events)
    cues = build_cues(events, insights, DURATION)
    assert len(cues) == len(insights)
    assert [c.second for c in cues] == sorted(c.second for c in cues)
    assert {c.insight_id for c in cues} == {i.id for i in insights}
    assert len({c.id for c in cues}) == len(cues)

def test_cues_never_expose_future_evidence():
    for seed in (0, 7, 42, 108):
        events = generate_events(seed)
        by_id = {e.id: e for e in events}
        cues = build_cues(events, generate_insights(events), DURATION)
        for cue in cues:
            assert cue.second < cue.until_second <= DURATION
            assert all(by_id[id].second <= cue.second for id in cue.evidence_event_ids)
            assert any(by_id[id].position == cue.focus for id in cue.evidence_event_ids)
            assert all(0 <= getattr(cue.focus, field) <= 100 for field in ('x', 'y'))

def test_api_delivers_broadcast_cues_with_matching_insights():
    data = client.get('/api/matches/demo?seed=7').json()
    assert 'cues' in data
    by_insight = {i['id']: i for i in data['insights']}
    assert data['cues']
    for cue in data['cues']:
        source = by_insight[cue['insight_id']]
        assert cue['second'] == source['second']
        assert cue['evidence_event_ids'] == source['evidence_event_ids']
        assert cue['metric_value'] == source['metric_value']
