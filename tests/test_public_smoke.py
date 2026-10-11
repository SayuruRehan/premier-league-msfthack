"""Offline contract tests for the actual hosted-site verification logic."""
import asyncio
import copy
import pytest
from scripts.export_static import build_bundle
from scripts.check_public_site import validate_content

HTML='<!doctype html><title>MatchShift AI</title><script type="module" src="./assets/index.js"></script>'


def test_public_smoke_accepts_actual_export(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","deterministic")
    replay,stories=asyncio.run(build_bundle())
    result=validate_content(HTML,replay,stories)
    assert result["stories"]==len(replay["insights"])*3
    assert result["events"]==len(replay["events"])


def test_public_smoke_rejects_missing_story_and_fabricated_metric(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","deterministic")
    replay,stories=asyncio.run(build_bundle())
    missing=copy.deepcopy(stories)
    missing.pop(next(iter(missing)))
    with pytest.raises(ValueError,match="every insight"):
        validate_content(HTML,replay,missing)

    corrupt=copy.deepcopy(replay)
    corrupt["cues"][0]["evidence_event_ids"]=[]
    with pytest.raises(ValueError,match="matching source evidence"):
        validate_content(HTML,corrupt,stories)


def test_public_smoke_rejects_non_static_site(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE","deterministic")
    replay,stories=asyncio.run(build_bundle())
    with pytest.raises(ValueError,match="expected static"):
        validate_content("This is the Azure placeholder",replay,stories)
