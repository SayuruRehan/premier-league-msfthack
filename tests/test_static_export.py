"""The standalone demo must contain truthful offline stories and their source events."""
import asyncio
from scripts.export_static import AUDIENCES, build_bundle, verify_bundle, write_bundle


def test_static_bundle_is_complete_and_grounded(tmp_path, monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "deterministic")
    replay, stories = asyncio.run(build_bundle(limit_insights=1))
    insight = replay["insights"][0]
    assert replay["synthetic"] is True
    assert all(stories[f"{insight['id']}:{a}"]["source"] == "deterministic"
               for a in AUDIENCES)
    assert all(stories[f"{insight['id']}:{a}"]["verified"] for a in AUDIENCES)
    assert len(stories) == len(AUDIENCES)


def test_rejects_static_export_when_real_inference_enabled(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "foundry_local")
    try:
        asyncio.run(build_bundle(limit_insights=1))
    except RuntimeError as error:
        assert "without hosted or local model inference" in str(error)
    else:
        raise AssertionError("Static build unexpectedly invoked dynamic model configuration")


def test_written_bundle_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_INFERENCE", "deterministic")
    replay, stories = asyncio.run(build_bundle())
    write_bundle(tmp_path, replay, stories)
    verify_bundle(tmp_path)
    assert len(stories) == len(replay["insights"]) * len(AUDIENCES)
