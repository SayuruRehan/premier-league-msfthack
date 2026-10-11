"""Anonymous public-site smoke check for the Azure Static Web Apps judge URL.

Never requires a deployment token or model/API credential. Tests actual served
HTML and JSON, not just a successful GitHub Actions deployment status.
"""
import argparse
import json
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

AUDIENCES = ("fan", "analyst", "broadcast")
TRACE_STAGES = ("TacticalAnalyst", "NarrativeDirector", "EvidenceVerifier", "AudienceAgent")


def validate_content(index_html: str, replay: dict, stories: dict) -> dict:
    if "<title>MatchShift AI" not in index_html or "./assets/" not in index_html:
        raise ValueError("Site did not serve the expected static MatchShift application")
    if replay.get("synthetic") is not True or replay.get("duration_seconds") != 5400:
        raise ValueError("Unexpected replay data; expected a fictional 90-minute match")
    if not replay.get("cues") or not replay.get("insights"):
        raise ValueError("Missing broadcast cues or tactical insights")
    events = {e["id"]: e for e in replay["events"]}
    insights = {i["id"]: i for i in replay["insights"]}
    if len(events) != len(replay["events"]):
        raise ValueError("Duplicate source event ID")
    if len(stories) != len(insights) * len(AUDIENCES):
        raise ValueError("Not every insight has all three persona stories")
    for cue in replay["cues"]:
        reference = insights.get(cue["insight_id"])
        if reference is None or cue["evidence_event_ids"] != reference["evidence_event_ids"]:
            raise ValueError("Broadcast cue is missing matching source evidence")
        if not cue["second"] <= cue["until_second"] <= replay["duration_seconds"]:
            raise ValueError("Broadcast cue is scheduled outside the match")
        if any(events[eid]["second"] > cue["second"] for eid in cue["evidence_event_ids"]):
            raise ValueError("Broadcast cue references a future event")
    for insight in insights.values():
        for audience in AUDIENCES:
            key = insight["id"] + ":" + audience
            story = stories.get(key)
            if not story:
                raise ValueError("Missing precomputed story: " + key)
            if not story["verified"] or story["source"] != "deterministic":
                raise ValueError("Static site contains unverified or undisclosed AI output")
            if story["insight_id"] != insight["id"] or story["audience"] != audience:
                raise ValueError("Static story is associated with the wrong audience/insight")
            if story["evidence_event_ids"] != insight["evidence_event_ids"]:
                raise ValueError("Static story evidence differs from trusted match evidence")
            if tuple(item["stage"] for item in story["trace"]) != TRACE_STAGES:
                raise ValueError("Missing Microsoft Agent Framework stage trace")
            if any(item["status"] == "rejected" for item in story["trace"]):
                raise ValueError("An unverified agent claim was published")
    return {"events":len(events),"insights":len(insights),"cues":len(replay["cues"]),"stories":len(stories)}


def validate_trust_demo(lab: dict, replay: dict) -> dict:
    """Validate the published *simulated* recovery evidence without a local model."""
    from packages.analytics.insights import generate_insights
    from packages.simulator.generator import generate_events
    from scripts.trust_lab import validate_trust_lab

    seed = int(replay["match_id"].split("-")[-1])
    if lab.get("seed") != seed:
        raise ValueError("Published trust lab does not match published replay")
    expected = {i.id: i for i in generate_insights(generate_events(seed))}
    validate_trust_lab(lab, expected)
    return {"failure_scenarios": len(lab["cases"])}


def fetch_text(url: str) -> str:
    request=Request(url, headers={"User-Agent": "MatchShift-public-smoke/1.0", "Accept": "*/*"})
    with urlopen(request,timeout=20) as response:
        if response.status != 200:
            raise ValueError(f"{url} returned HTTP {response.status}")
        return response.read(3_000_000).decode("utf-8")


def check_public_site(
    base_url: str, attempts: int = 8, retry_seconds: float = 7,
    require_trust_lab: bool = False,
) -> dict:
    parts = urlsplit(base_url)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
        raise ValueError("Public URL must be a valid HTTPS site URL")
    root=base_url.rstrip("/")+"/"
    error=None
    for attempt in range(1,attempts+1):
        try:
            index=fetch_text(root)
            replay=json.loads(fetch_text(urljoin(root,"data/replay.json")))
            stories=json.loads(fetch_text(urljoin(root,"data/stories.json")))
            stats=validate_content(index,replay,stories)
            if require_trust_lab:
                trust_lab=json.loads(fetch_text(urljoin(root,"data/trust_lab.json")))
                stats.update(validate_trust_demo(trust_lab,replay))
            return stats
        except (ValueError,KeyError,AssertionError,URLError,HTTPError,UnicodeDecodeError,TypeError,TimeoutError) as exc:
            error=exc
            print(f"Attempt {attempt}/{attempts}: public-site verification not ready: {exc}",flush=True)
            if attempt<attempts:
                time.sleep(retry_seconds)
    raise RuntimeError(f"Public MatchShift site did not pass smoke test: {error}")


def main() -> None:
    parser=argparse.ArgumentParser(description="Verify the deployed public Azure MatchShift site")
    parser.add_argument("--url", required=True)
    parser.add_argument("--attempts",type=int,default=8)
    parser.add_argument("--retry-seconds",type=float,default=7)
    parser.add_argument("--require-trust-lab", action="store_true",
                        help="Validate published model-failure simulations as well")
    args=parser.parse_args()
    if args.attempts<1 or args.retry_seconds<0:
        parser.error("Attempts must be positive and retry interval nonnegative")
    stats=check_public_site(args.url,args.attempts,args.retry_seconds,args.require_trust_lab)
    print(f"PASS: publicly served demo verified: {stats}")


if __name__=="__main__":
    main()
