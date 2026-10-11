"""Loopback restriction and input validation apply before constructing an Agent."""
import pytest
from packages.agents.local_endpoint import get_local_config


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:5273/v1/",
    "http://public.example.com:5273/v1/",
    "http://127.0.0.1:5273/admin/",
    "http://localhost/v1/",
    "http://localhost:5273/v1/?payload=1",
    "http://localhost:5273/v1/#fragment",
    "http://name:secret@127.0.0.1:5273/v1/",
    "file:///tmp/model",
    "http://127.0.0.1:0/v1/"
])
def test_endpoint_rejects_unsafe_configuration(monkeypatch,url):
    monkeypatch.setenv("MATCHSHIFT_LOCAL_URL",url)
    with pytest.raises(ValueError):
        get_local_config()


def test_endpoint_normalizes_local_v1(monkeypatch):
    monkeypatch.setenv("MATCHSHIFT_LOCAL_URL","http://127.0.0.1:5273/v1")
    monkeypatch.setenv("MATCHSHIFT_LOCAL_MODEL","phi-4-mini")
    config=get_local_config()
    assert config.base_url=="http://127.0.0.1:5273/v1/"
    assert config.model=="phi-4-mini"
