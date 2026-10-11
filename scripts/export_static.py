"""Export a complete self-contained, verifiable MatchShift judging demo.

This command performs *real* Microsoft Agent Framework runs in deterministic mode,
then freezes the approved output to JSON. Static visitors do not call an API,
an AI endpoint, or a paid service. Never label frozen responses as live inference.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path

from packages.agents.contracts import StoryRequest
from packages.agents.workflow import run_story
from services.api.app.main import demo

AUDIENCES = ("fan", "analyst", "broadcast")


async def build_bundle(seed: int = 7, limit_insights: int | None = None) -> tuple[dict, dict]:
    if os.getenv("MATCHSHIFT_INFERENCE", "deterministic").lower() != "deterministic":
        raise RuntimeError("Static bundle must be generated without hosted or local model inference")
    replay = demo(seed=seed).model_dump(mode="json")
    insights = replay["insights"]
    if limit_insights is not None:
        insights = insights[:limit_insights]
    original_ids = {event["id"] for event in replay["events"]}
    stories: dict[str, dict] = {}

    for insight in insights:
        for audience in AUDIENCES:
            response = await run_story(StoryRequest(
                seed=seed, insight_id=insight["id"], audience=audience,
            ))
            story = response.model_dump(mode="json")
            key = f"{insight['id']}:{audience}"
            if not story["verified"] or story["source"] != "deterministic":
                raise ValueError(f"Refusing unverified or model-generated static story: {key}")
            if story["insight_id"] != insight["id"] or story["evidence_event_ids"] != insight["evidence_event_ids"]:
                raise ValueError(f"Static story does not match source insight: {key}")
            if any(event_id not in original_ids for event_id in story["evidence_event_ids"]):
                raise ValueError(f"Unknown evidence event in static story: {key}")
            if not story["trace"] or any(stage["status"] == "rejected" for stage in story["trace"]):
                raise ValueError(f"Unexpected execution trace in static story: {key}")
            stories[key] = story
    return replay, stories


def write_bundle(output: Path, replay: dict, stories: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "replay.json").write_text(
        json.dumps(replay, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "stories.json").write_text(
        json.dumps(stories, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8"
    )


def verify_bundle(output: Path) -> None:
    replay = json.loads((output / "replay.json").read_text(encoding="utf-8"))
    stories = json.loads((output / "stories.json").read_text(encoding="utf-8"))
    assert replay["synthetic"] is True
    assert replay["cues"]
    assert replay["insights"]
    by_id = {event["id"]: event for event in replay["events"]}
    assert len(stories) == len(replay["insights"]) * len(AUDIENCES)
    for cue in replay["cues"]:
        assert cue["second"] <= cue["until_second"]
        assert all(by_id[event_id]["second"] <= cue["second"]
                   for event_id in cue["evidence_event_ids"])
    for insight in replay["insights"]:
        for audience in AUDIENCES:
            story = stories[f"{insight['id']}:{audience}"]
            assert story["verified"] and story["source"] == "deterministic"
            assert story["evidence_event_ids"] == insight["evidence_event_ids"]
            assert [t["stage"] for t in story["trace"]] == [
                "TacticalAnalyst", "NarrativeDirector", "EvidenceVerifier", "AudienceAgent"
            ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an offline MatchShift judging bundle")
    parser.add_argument("--output", type=Path, default=Path("apps/web/public/data"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify_bundle(args.output)
    else:
        replay, stories = asyncio.run(build_bundle(seed=args.seed))
        write_bundle(args.output, replay, stories)
        verify_bundle(args.output)
    print(f"Validated MatchShift static replay and stories at {args.output}")


if __name__ == "__main__":
    main()
