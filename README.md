# MatchShift AI

**Explainable football match intelligence, powered by synthetic events.** Built for the Premier League × Microsoft hackathon.

This foundation delivers a reproducible synthetic match replay, a FastAPI endpoint, a React pitch/timeline viewer, and evidence-backed deterministic insights. Microsoft Agent Framework / Foundry Local integration is the next milestone; **no AI service is claimed or invoked in this version**.

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
- `GET /api/matches/demo`: deterministic complete synthetic match, including score, frames, events and insights
- `GET /api/matches/demo?seed=12`: seeded variation (same seed => same result)

## Tests

```sh
pip install -r services/api/requirements-dev.txt
pytest -q
cd apps/web && npm ci && npm run build
```

## Architecture

- `packages/simulator`: seeded event simulator and Pydantic contracts.
- `packages/analytics`: evidence-based rolling analysis, no generative AI yet.
- `services/api`: FastAPI JSON replay service.
- `apps/web`: football pitch replay, scoreline, evidence and timeline.

All clubs, players, and match actions are **fictional and synthetic**; no licensed league feeds or match footage are used. See `docs/architecture.md` for the next agentic milestones.
