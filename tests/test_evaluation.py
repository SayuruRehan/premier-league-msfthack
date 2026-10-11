"""The evaluation report must be reproducible and refuse inference by accident."""
import asyncio
from unittest.mock import patch

import pytest
from scripts.evaluate import evaluate,evaluate_seed,markdown
from scripts.probe_foundry_local import probe


def test_multiple_synthetic_scenarios_have_grounded_insights():
    summary=[evaluate_seed(i) for i in (0,7,12,42,100)]
    assert all(case["events"]==180 and case["goals"]==3 for case in summary)
    assert all(case["insights"]>=3 for case in summary)
    assert len({case["match_event_sha256"] for case in summary})==5
    assert any(case["tactical_shift_insights"]>0 for case in summary)


def test_model_free_evaluation_and_recovery_are_auditable(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","deterministic")
    result=asyncio.run(evaluate((7,12)))
    assert result["seed_count"]==2
    assert result["totals"]["simulated_events"]==360
    assert result["totals"]["verified_persona_stories"]>0
    assert result["totals"]["failures"]==0
    assert result["recovery"]["invalid_director_angle_rejected"]
    assert result["recovery"]["invalid_audience_style_rejected"]
    assert result["recovery"]["provider_outage_recovered"]
    assert not result["model_validation"]["real_phi_inference_exercised"]
    document=markdown(result)
    assert "not" in document.lower() and "real Phi inference" in document


def test_evaluation_rejects_real_model_configuration(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","foundry_local")
    with pytest.raises(RuntimeError,match="cannot use live inference"):
        asyncio.run(evaluate((7,)))


def test_real_phi_probe_cannot_pass_on_fallback(monkeypatch):
    import packages.agents.workflow as module
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","foundry_local")
    async def unavailable(_analysis):
        raise ConnectionError("No local Phi runtime available in CI")
    with patch.object(module,"choose_with_foundry_local",unavailable):
        with pytest.raises(RuntimeError,match="was NOT proven"):
            asyncio.run(probe(7,"broadcast"))


def test_real_phi_probe_refuses_deterministic_mode(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","deterministic")
    with pytest.raises(RuntimeError,match="MATCHSHIFT_INFERENCE"):
        asyncio.run(probe(7,"broadcast"))
