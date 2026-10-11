"""Tests execute Microsoft's workflow, including rejection and recovery."""
import asyncio
from fastapi.testclient import TestClient
from services.api.app.main import app
from packages.agents.contracts import DirectorDecision, StoryRequest
from packages.agents.workflow import evidence_verifier, tactical_analyst

client = TestClient(app)
INSIGHT = "insight-evt-1740"

def test_agent_config_defaults(monkeypatch):
    monkeypatch.delenv("MATCHSHIFT_INFERENCE", raising=False)
    data = client.get("/api/agents/config").json()
    assert data["framework"] == "Microsoft Agent Framework"
    assert data["inference_mode"] == "deterministic"
    assert data["local_only"] is True

def test_real_workflow_runs_and_provenance(monkeypatch):
    monkeypatch.delenv("MATCHSHIFT_INFERENCE", raising=False)
    response = client.get(f"/api/matches/demo/story?insight_id={INSIGHT}")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True and data["source"] == "deterministic"
    assert data["framework"] == "Microsoft Agent Framework"
    assert [t["stage"] for t in data["trace"]] == [
        "TacticalAnalyst", "NarrativeDirector", "EvidenceVerifier", "AudienceAgent"
    ]
    assert data["trace"][2]["status"] == "approved"
    assert data["evidence_event_ids"][-1] == "evt-1740"
    assert set(data["evidence_event_ids"]) <= {
        e["id"] for e in client.get("/api/matches/demo").json()["events"]
    }

def test_three_audiences_with_same_evidence(monkeypatch):
    monkeypatch.delenv("MATCHSHIFT_INFERENCE", raising=False)
    responses = {
        a: client.get(f"/api/matches/demo/story?insight_id={INSIGHT}&audience={a}")
        for a in ("fan", "analyst", "broadcast")
    }
    assert all(r.status_code == 200 for r in responses.values())
    data = {aud: r.json() for aud, r in responses.items()}
    assert len({o["narration"] for o in data.values()}) == 3
    assert len({tuple(o["evidence_event_ids"]) for o in data.values()}) == 1
    assert all(o["verified"] for o in data.values())

def test_invalid_insight_and_audience():
    assert client.get("/api/matches/demo/story?insight_id=not-found").status_code == 404
    assert client.get(f"/api/matches/demo/story?insight_id={INSIGHT}&audience=invalid").status_code == 422

def test_hallucinated_angle_is_rejected_and_recovered(monkeypatch):
    import packages.agents.workflow as module
    async def bad_model(_analysis):
        return "the referee awarded 57 imaginary penalties"
    monkeypatch.setattr(module, "choose_with_foundry_local", bad_model)
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "foundry_local")
    response = client.get(f"/api/matches/demo/story?insight_id={INSIGHT}")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True and data["source"] == "fallback"
    assert any(t["status"] == "rejected" for t in data["trace"])
    assert any(t["status"] == "fallback" for t in data["trace"])
    assert "penalties" not in data["narration"]

def test_offline_fallback_is_transparent(monkeypatch):
    import packages.agents.workflow as module
    async def unavailable(_analysis):
        raise ConnectionError("unavailable")
    monkeypatch.setattr(module, "choose_with_foundry_local", unavailable)
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "foundry_local")
    response = client.get(f"/api/matches/demo/story?insight_id={INSIGHT}")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback" and data["verified"] is True
    assert data["trace"][1]["status"] == "fallback"

def test_verifier_rejects_tampered_evidence():
    async def check():
        analysis = await tactical_analyst(StoryRequest(seed=7, insight_id=INSIGHT))
        altered = analysis.model_copy(update={"metric_value": analysis.metric_value + 99})
        return await evidence_verifier(DirectorDecision(
            analysis=altered, angle="scoreline", source="deterministic", note="test"
        ))
    verdict = asyncio.run(check())
    assert verdict.approved is False
    assert "source data" in verdict.reason

def test_foundry_uses_two_model_backed_specialists_with_verified_templates(monkeypatch):
    import packages.agents.workflow as module
    async def approved_angle(_analysis):
        return "scoreline"
    async def approved_style(_analysis, _audience):
        return "excited"
    monkeypatch.setattr(module, "choose_with_foundry_local", approved_angle)
    monkeypatch.setattr(module, "choose_style_with_foundry_local", approved_style)
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "foundry_local")
    response = client.get(f"/api/matches/demo/story?insight_id={INSIGHT}&audience=broadcast")
    assert response.status_code == 200
    story = response.json()
    assert story["source"] == "foundry_local"
    assert story["style_source"] == "foundry_local"
    assert story["presentation_style"] == "excited"
    assert story["verified"] is True
    assert "A turning point in this simulated match!" in story["narration"]
    assert story["trace"][-1]["stage"] == "AudienceAgent"

def test_invalid_audience_model_output_cannot_enter_story(monkeypatch):
    import packages.agents.workflow as module
    async def approved_angle(_analysis):
        return "scoreline"
    async def unsafe_style(_analysis, _audience):
        return "the away team secretly has 22 goals"
    monkeypatch.setattr(module, "choose_with_foundry_local", approved_angle)
    monkeypatch.setattr(module, "choose_style_with_foundry_local", unsafe_style)
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "foundry_local")
    response = client.get(f"/api/matches/demo/story?insight_id={INSIGHT}&audience=broadcast")
    assert response.status_code == 200
    story = response.json()
    assert story["verified"] is True
    assert story["source"] == "foundry_local"
    assert story["style_source"] == "fallback"
    assert story["presentation_style"] == "excited"
    assert "22 goals" not in story["narration"]
