"""Real framework workflow tests with deterministic mocked provider answers."""
import asyncio
import copy

import pytest

from packages.analytics.insights import generate_insights
from packages.simulator.generator import generate_events
from scripts.trust_lab import build_trust_lab, validate_trust_lab, CASES


def test_every_failure_mode_recovers_without_publishing_fake_claims(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "deterministic")
    lab=asyncio.run(build_trust_lab(seed=7))
    assert lab["live_model_inference"] is False
    assert lab["simulated_failure_tests"] is True
    assert set(lab["cases"])==set(CASES)
    expected={i.id:i for i in generate_insights(generate_events(7))}
    validate_trust_lab(lab,expected)
    assert lab["cases"]["fabricated_claim"]["story"]["source"]=="fallback"
    assert any(item["status"]=="rejected"
               for item in lab["cases"]["fabricated_claim"]["story"]["trace"])
    assert lab["cases"]["provider_outage"]["story"]["source"]=="fallback"
    assert lab["cases"]["invalid_style"]["story"]["style_source"]=="fallback"


def test_trust_lab_fails_on_tampered_evidence(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "deterministic")
    lab=asyncio.run(build_trust_lab(seed=7))
    expected={i.id:i for i in generate_insights(generate_events(7))}
    tampered=copy.deepcopy(lab)
    tampered["cases"]["provider_outage"]["story"]["evidence_event_ids"]=[]
    with pytest.raises(ValueError,match="unverified or tampered"):
        validate_trust_lab(tampered,expected)


def test_trust_lab_rejects_misleading_live_model_claim(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "deterministic")
    lab=asyncio.run(build_trust_lab(seed=7))
    expected={i.id:i for i in generate_insights(generate_events(7))}
    lab["live_model_inference"]=True
    with pytest.raises(ValueError,match="simulated"):
        validate_trust_lab(lab,expected)
