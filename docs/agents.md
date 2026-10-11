# MatchShift agent workflow (Milestone 3)

## Actual Microsoft integration

The backend executes `@workflow(name="MatchShiftStoryPipeline")` from Microsoft's **agent-framework-core**. Each specialized role is a named `@step` with a typed Pydantic handoff. This is not a fake JavaScript animation or a set of hardcoded trace labels: the HTTP endpoint runs the framework workflow for each requested insight.

| Stage | Function | Output |
|---|---|---|
| TacticalAnalyst | Extracts and checks source match insight | Analysis with evidence event IDs |
| NarrativeDirector | Proposes the narrative angle | Scoreline / momentum / evidence |
| EvidenceVerifier | Recomputes every numeric fact and validates evidence IDs | Approve or reject |
| AudienceAgent | Produces vetted fan / analyst / broadcast copy | StoryResponse |

When `MATCHSHIFT_INFERENCE=foundry_local`, a **second model-backed AudienceStyleAgent** selects an allowed presentation-style token within the AudienceAgent stage. It cannot write source claims. Its decision is recorded separately through `presentation_style` and `style_source`. If the style output is unsupported or times out, a deterministic template is used and this role records `style_source=fallback`.

A rejected angle triggers one **bounded replan** with the deterministic safe option; no verified facts are overwritten. If local AI inference is unavailable, the request succeeds using transparent `source=fallback`. This remains an intentionally *hybrid* workflow: two optional model-backed decisions and deterministic analysis, verification and final wording. No model is allowed to write unverified free-form match claims. We can expand generative roles after hardening the verifier.

## Zero-cost default (no model or cloud account required)

```bash
pip install -r services/api/requirements.txt
uvicorn services.api.app.main:app --reload
# Browser: http://localhost:5173 (frontend needs npm install && npm run dev)
```

By default `MATCHSHIFT_INFERENCE=deterministic`. Agent Framework orchestration runs, but the narrative angles and wording are deterministic. The user interface labels this correctly.

## Optional Microsoft Foundry Local / Phi inference (no cloud billing)

Install and run Foundry Local with a compatible downloadable chat model (model identifiers depend on the hardware and installed model). Inspect its status and **local OpenAI-compatible chat endpoint**. Then:

```bash
pip install -r services/api/requirements-local.txt
export MATCHSHIFT_INFERENCE=foundry_local
export MATCHSHIFT_LOCAL_URL=http://127.0.0.1:5273/v1/
export MATCHSHIFT_LOCAL_MODEL=phi-4-mini
uvicorn services.api.app.main:app --reload
```

The URL above is **illustrative**: use the actual port and model ID reported by your local Foundry runtime. We deliberately restrict model URLs to loopback `http` endpoints and timeout after 12 seconds. The optional package `agent-framework-openai` is used through `Agent(client=OpenAIChatCompletionClient(...))`, which supports the chat-completions endpoint exposed by Foundry Local. Nothing connects to a paid cloud service.

## API

- `GET /api/agents/config` — framework name, selected mode (no secrets).
- `GET /api/matches/demo/story?seed=7&insight_id=insight-evt-1740&audience=fan` — runs the workflow and returns a story, provenance, and auditable trace.
- `audience`: `fan`, `analyst` or `broadcast`.

The `evidence_event_ids` returned can be looked up against `GET /api/matches/demo?seed=7`. There is no LLM-generated unverified statistic. This demo currently reasons over scripted fictional match events only, not real Premier League data or footage.

## Engineering constraints

- API callers cannot select the inference provider or arbitrary model URL; only server configuration controls the provider.
- Safe fallback after model failure is explicitly identified as `source=fallback`.
- No private model keys or prompts are exposed in API responses.
- Isolate workflows per request; tests cover rejection and recovery, valid IDs, and persona separation.
- Microsoft's functional workflow API is currently documented as experimental, so keep dependencies under version constraints and re-check compatibility before the final submission.
