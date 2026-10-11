"""Real Agent Framework -> real HTTP client -> local fake chat endpoint.

This does NOT run Phi or Foundry Local. It exercises the complete wire
protocol and both specialist roles without patching decision functions,
so provider breaking changes surface in CI.
"""
import asyncio
import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from importlib.metadata import PackageNotFoundError, version

try:
    version("agent-framework-openai")
except PackageNotFoundError:
    pytest.skip("Optional agent-framework-openai provider is not installed in the core-only job",
                allow_module_level=True)

pytest.importorskip("agent_framework.openai")

from packages.agents.contracts import StoryRequest
from packages.agents.workflow import run_story
from scripts.check_foundry_endpoint import discover_models


@contextmanager
def model_stub():
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/v1/models":
                self.send_error(404)
                return
            payload={"object":"list","data":[{"id":"phi-test-stub","object":"model","owned_by":"unit-test"}]}
            data=json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if self.path != "/v1/chat/completions":
                self.send_error(404)
                return
            size=int(self.headers.get("Content-Length","0"))
            body=json.loads(self.rfile.read(size).decode())
            requests.append(body)
            assert body["model"] == "phi-test-stub"
            prompt=json.dumps(body.get("messages",[]))
            is_style = "Select the safest presentation style" in prompt
            value = "excited" if is_style else "scoreline"
            response={
                "id":"chatcmpl-testing-local-stub",
                "object":"chat.completion",
                "created":1728000000,
                "model":"phi-test-stub",
                "choices":[{"index":0,"message":{"role":"assistant","content":value},"finish_reason":"stop"}],
                "usage":{"prompt_tokens":15,"completion_tokens":1,"total_tokens":16}
            }
            data=json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1/",requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_actual_agent_framework_openai_http_transport(monkeypatch):
    with model_stub() as (url,calls):
        monkeypatch.setenv("MATCHSHIFT_INFERENCE","foundry_local")
        monkeypatch.setenv("MATCHSHIFT_LOCAL_URL",url)
        monkeypatch.setenv("MATCHSHIFT_LOCAL_MODEL","phi-test-stub")
        discovered=discover_models()
        assert discovered["configured_model_advertised"] is True
        assert discovered["advertised_models"] == ["phi-test-stub"]

        story=asyncio.run(run_story(StoryRequest(
            seed=7,insight_id="insight-evt-1740",audience="broadcast"
        )))
        assert story.verified is True
        assert story.source == "foundry_local"
        assert story.style_source == "foundry_local"
        assert story.angle == "scoreline"
        assert story.presentation_style == "excited"
        assert len(calls) == 2, "Both specialist roles must send genuine HTTP requests"
        assert all(c["model"]=="phi-test-stub" for c in calls)
        assert [s.stage for s in story.trace]==[
            "TacticalAnalyst","NarrativeDirector","EvidenceVerifier","AudienceAgent"
        ]
        assert "200 goals" not in story.narration


def test_diagnostic_rejects_unreachable_endpoint(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_LOCAL_URL","http://127.0.0.1:1/v1/")
    monkeypatch.setenv("MATCHSHIFT_LOCAL_MODEL","phi-test-stub")
    with pytest.raises(RuntimeError,match="Could not list local models"):
        discover_models()
