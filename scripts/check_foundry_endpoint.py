"""Read-only, local-only diagnostics before attempting a real Foundry Local run.

Checks the OpenAI-compatible /v1/models API. Discovering an endpoint is NOT
proof that it is Foundry Local or that it is running a genuine Phi model.
"""
import argparse
import json
from urllib.request import Request, urlopen
from packages.agents.local_endpoint import get_local_config


def discover_models() -> dict:
    config = get_local_config()
    request = Request(config.base_url + "models", headers={"Accept":"application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read(300_000).decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(
            "Could not list local models. Run 'foundry server status' and load a model "
            "with your Foundry CLI, then set MATCHSHIFT_LOCAL_URL to the displayed "
            "loopback /v1 endpoint."
        ) from exc
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise RuntimeError("Local endpoint did not respond with OpenAI-compatible /v1/models data")
    names = [item["id"] for item in rows if isinstance(item,dict) and isinstance(item.get("id"),str)]
    return {"endpoint":config.base_url, "configured_model":config.model,
            "advertised_models": names, "configured_model_advertised":config.model in names}


def main() -> None:
    parser=argparse.ArgumentParser(description="Diagnose local /v1/models; never calls an external model provider")
    args=parser.parse_args()
    _=args
    data=discover_models()
    print(json.dumps(data,indent=2))
    if not data["advertised_models"]:
        print("No models are currently advertised. Load your chosen model and try again.")
        raise SystemExit(1)
    if not data["configured_model_advertised"]:
        print("The configured model is not advertised. Set MATCHSHIFT_LOCAL_MODEL to the served model ID.")
        raise SystemExit(2)
    print("Endpoint is reachable; this check does not attest model authenticity. Run the end-to-end probe next.")


if __name__=="__main__":
    main()
