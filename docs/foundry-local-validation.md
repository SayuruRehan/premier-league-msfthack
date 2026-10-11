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
