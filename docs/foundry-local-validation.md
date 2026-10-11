# Reproducibly prove real Microsoft Foundry Local / Phi inference

**Current status:** The Azure-hosted demo is verified, but **actual hardware-backed Phi inference has not yet been proven**. Our CI uses deterministic or mocked provider responses. To claim live local AI, run this opt-in probe on a compatible machine.

## Setup (macOS Apple Silicon)

Microsoft's current Foundry Local CLI preview documents these Homebrew commands for Apple Silicon:

```sh
brew tap microsoft/foundrylocal
brew install foundrylocal
foundry --version
foundry model list
foundry model info phi-4-mini
foundry model download phi-4-mini
foundry chat phi-4-mini
```

Close the interactive prompt, then inspect `foundry server status` to get the **actual loopback endpoint**. Check whether the Phi model remains served after leaving chat, and refer to `foundry --help` for installed-version-specific commands if needed.

Microsoft's official source: https://learn.microsoft.com/en-us/azure/foundry-local/how-to/how-to-use-foundry-local-cli

On Windows the documented installer is `winget install Microsoft.FoundryLocal`. Verify hardware/model compatibility and runtime availability before using any example model ID.

## Run an actual end-to-end probe

At the project root, using your locally reported model name and server address:

```sh
python -m pip install -r services/api/requirements-local.txt

export MATCHSHIFT_INFERENCE=foundry_local
export MATCHSHIFT_LOCAL_URL=http://127.0.0.1:5273/v1/
export MATCHSHIFT_LOCAL_MODEL=phi-4-mini

python -m scripts.probe_foundry_local --seed 7 --audience broadcast
```

**Replace the URL and model ID** with those reported by your installed runtime. Port 5273 is only an illustration. The model URL must resolve to loopback over HTTP, not an external host. The script is fail-closed and requires BOTH roles to return valid local-model decisions and pass verification. If either role falls back or returns an invalid token, the probe exits unsuccessfully, so the success report cannot be faked by deterministic operation.

On success the script writes `artifacts/foundry-local-probe.json`. It includes the role provenance, chosen angle/style, seed, evidence event IDs and end-to-end latency. Inspect it before sharing; do **not** commit keys, personal device details or logs containing private values.

## Troubleshooting

- **Import error for OpenAI client:** Verify `agent-framework-openai` installed from the optional local requirements file.
- **Timeout / connection refused:** Verify the server is running; use `foundry server status`. Check the model is actually loaded.
- **Model not found:** Use the identifier shown by `foundry model list` and the runtime's exposed chat-completions model ID, not an invented deployment name.
- **Fallback provenance:** This means real local inference was **not** proven; check the provider endpoint and its returned text. Both model roles require a single token from a small allowlist.
- **Apple Intel macOS:** The Homebrew instructions above explicitly target Apple Silicon, not Intel Macs; use a supported machine or keep the already working free deterministic route.

Even after successful local validation, **the public Azure demo still uses precomputed deterministic stories**. It is not a hosted generative endpoint and should not be described as such.

## Phase 1 — verify the served local endpoint (no model inference)

Microsoft's CLI supports directly loading a model and starting the daemon, and the Agent Framework's `OpenAIChatCompletionClient` supports the same `/v1/chat/completions` surface.

```sh
foundry model list --type chat
foundry model info phi-4-mini
foundry model download phi-4-mini
foundry server start --port 39839 --idle-timeout 0
foundry model load phi-4-mini
foundry server status
foundry model list --loaded
```

If you already have a running daemon, use `foundry server restart --port 39839 --idle-timeout 0` instead of `start`. The port `39839` is an optional fixed-port example; read the actual service URL from `foundry server status`.

Then configure the **actual** local endpoint and model ID (not necessarily the alias):

```sh
python -m pip install -r services/api/requirements-local.txt
export MATCHSHIFT_LOCAL_URL=http://127.0.0.1:39839/v1/
export MATCHSHIFT_LOCAL_MODEL=phi-4-mini
python -m scripts.check_foundry_endpoint
```

The diagnostic requests `GET /v1/models` over **loopback HTTP only** and prints the server-advertised model IDs. If the alias isn't advertised, set `MATCHSHIFT_LOCAL_MODEL` to a listed served ID and re-run. The service may take time to load the model. No API key or paid Azure resource is required.

## Phase 2 — validate the actual model decisions

```sh
export MATCHSHIFT_INFERENCE=foundry_local
python -m scripts.probe_foundry_local --seed 7 --audience broadcast
```

The full Microsoft Agent Framework workflow should select an allowed narrative angle and audience style through **two local HTTP chat-completion requests**, then verify its claims. The probe **fails** if either agent falls back. Record the measured latency and accepted decisions, and capture the local `foundry server status` and `foundry model list --loaded` as separate evidence of the serving runtime.

The CLI must be run on your own supported computer. An arbitrary custom server can imitate `/v1/models` and `/v1/chat/completions`; **these endpoint tests alone cannot cryptographically attest model identity or prove hardware execution**. Check the running Foundry process and loaded model separately before describing it as genuine Phi inference.

## Automated integration coverage (CI)

Our isolated GitHub Actions `foundry_transport` job runs the **real Microsoft Agent Framework `Agent` objects and `OpenAIChatCompletionClient` network transport** against a temporary OpenAI-compatible stub server bound to `127.0.0.1`. It checks `GET /v1/models`, both specialist requests, typed role outputs, evidence verification, and allowlisted decisions. The stub clearly identifies itself as `phi-test-stub`.

**A green CI transport job is proof of client/protocol compatibility, not real Phi weights or Foundry Local running in GitHub Actions.**

Docs: https://learn.microsoft.com/en-us/azure/foundry-local/reference/reference-cli
and https://learn.microsoft.com/en-us/agent-framework/hosting/self-hosting/openai-endpoints
