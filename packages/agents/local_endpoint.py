"""Validated loopback-only OpenAI-compatible endpoint for Foundry Local.

Never accepts remote addresses, arbitrary URL paths, credentials, or query
strings. Browser/public deployment never calls this module.
"""
import os
from dataclasses import dataclass
from urllib.parse import urlsplit

@dataclass(frozen=True)
class LocalModelConfig:
    base_url: str
    model: str


def get_local_config() -> LocalModelConfig:
    raw = os.environ.get("MATCHSHIFT_LOCAL_URL", "http://127.0.0.1:5273/v1/")
    parts = urlsplit(raw)
    if (
        parts.scheme != "http"
        or parts.hostname not in ("localhost", "127.0.0.1", "::1")
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or parts.path.rstrip("/") != "/v1"
        or parts.port is None
        or not 1 <= parts.port <= 65535
    ):
        raise ValueError("Foundry endpoint must be http://127.0.0.1:<port>/v1/ (or localhost / [::1])")
    model = os.environ.get("MATCHSHIFT_LOCAL_MODEL", "phi-4-mini").strip()
    if not model or len(model) > 200 or any(ord(c) < 32 for c in model):
        raise ValueError("MATCHSHIFT_LOCAL_MODEL must be a valid model identifier")
    return LocalModelConfig(base_url=raw.rstrip("/") + "/", model=model)
