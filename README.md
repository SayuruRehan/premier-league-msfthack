# MatchShift AI

**Explainable football match intelligence, powered by synthetic events.** Built for the Premier League × Microsoft hackathon.

This prototype delivers a reproducible synthetic match replay, a FastAPI endpoint, a React pitch/timeline viewer, rolling tactical metrics, possession-chain summaries and evidence-backed deterministic insights. Microsoft Agent Framework now orchestrates a four-stage evidence-verified storytelling workflow. **No paid AI service is needed**: the default runs deterministically, with optional genuine local Phi inference through Microsoft Foundry Local.

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
cd apps/web && npm ci && npm run build
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
