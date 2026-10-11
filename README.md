# MatchShift AI

**Explainable football match intelligence, powered by synthetic events.** Built for the Premier League × Microsoft hackathon.

This prototype delivers a reproducible synthetic match replay, a FastAPI endpoint, a React pitch/timeline viewer, rolling tactical metrics, possession-chain summaries and evidence-backed deterministic insights. Microsoft Agent Framework now orchestrates a four-stage evidence-verified storytelling workflow. **No paid AI service is needed**: the default runs deterministically, with optional genuine local Phi inference through Microsoft Foundry Local for the Narrative Director **and** Audience Style roles.

## Quick start

Python 3.11+:

```sh
python -m pip install -r services/api/requirements.txt
uvicorn services.api.app.main:app --reload
```

Then run the React UI in another terminal (Node 20+):

```sh
cd apps/web
npm install
npm run dev
```

Visit http://localhost:5173. API docs: http://localhost:8000/docs.

## API

- `GET /health`: service health
- `GET /api/matches/demo`: deterministic complete synthetic match, including score, events, possession chains, rolling snapshots and insights
- `GET /api/matches/demo?seed=12`: seeded variation (same seed => same result)
- `GET /api/agents/config`: current workflow and inference mode
- `GET /api/matches/demo/story?seed=7&insight_id=insight-evt-1740&audience=fan`: run the four-stage agent workflow

## Tests

```sh
pip install -r services/api/requirements-dev.txt
pytest -q
cd apps/web && npm install && npm run build
```

## Architecture

- `packages/simulator`: seeded event simulator and Pydantic contracts.
- `packages/analytics`: coherent possession chains, rolling five-minute metrics and evidence-grounded tactical-shift detection. See `docs/analytics.md` for signal definitions and limitations.
- `packages/agents`: Microsoft Agent Framework multi-stage orchestration, verified evidence and optional Foundry Local Phi decision agent. See `docs/agents.md`.
- `services/api`: FastAPI JSON replay and agent endpoints.
- `apps/web`: football pitch replay, scoreline, evidence and timeline.

All clubs, players, and match actions are **fictional and synthetic**; no licensed league feeds or match footage are used. See `docs/architecture.md` for the next agentic milestones.

## Optional local AI model

No Azure account, subscription or GPU is required for the default verified workflow. To enable genuine local model decisions, install `services/api/requirements-local.txt` and configure `MATCHSHIFT_INFERENCE=foundry_local`. See `docs/agents.md` for safety rules, model IDs and setup.

## Broadcast experience

The cinematic broadcast canvas displays event-backed lower thirds, spotlighted pitch positions and recent passing trajectories. The clickable director's cue sheet and replay timeline navigate goals and tactical changes. Every on-screen cue has a start time, focus point, numerical metric and exact evidence IDs from synthetic events. `GET /api/matches/demo` now includes `cues`.

The default mode is fully offline/deterministic. Optional Phi Local reasoning selects only narrative **angles** and **presentation styles**; a verifier rejects mismatched source facts and final story copy is emitted from trusted templates. This keeps a demo free to run without overstating model autonomy.

## Judge-ready public demo (Milestone 5)

Run at the repository root to generate a self-contained, validated offline snapshot of **every** synthetic insight in all three audience modes:

```sh
python -m pip install -r services/api/requirements.txt
python -m scripts.export_static --output apps/web/public/data
cd apps/web
npm install
VITE_STATIC_DEMO=true npm run build
```

The resulting `apps/web/dist` directory can be hosted as plain static files on **Azure Static Web Apps Free** or **GitHub Pages**. Public visitors never contact FastAPI, Foundry Local, a model provider, or an Azure AI endpoint. Static JSON is precomputed from real Agent Framework workflows with the no-model deterministic provider, and labeled accordingly. Local API plus live Microsoft Agent Framework execution remains the default development mode.

The workflow `.github/workflows/deploy-azure-static.yml` builds and validates the static site on every push to `master` but does not deploy until `AZURE_STATIC_WEB_APPS_API_TOKEN` is configured. The GitHub Pages fallback `.github/workflows/deploy-pages.yml` also requires enabling **GitHub Actions** as the repository's Pages source. See `docs/deployment.md`.
