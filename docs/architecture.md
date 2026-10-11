# MatchShift Architecture and Roadmap

## Foundation (this PR)

- Event contract: Pydantic MatchEvent with normalized location (0–100 on each axis).
- 90-minute simulated replay of fictional Northbridge FC vs Harbor City, seeded for reproducibility.
- Scripted goals at 29', 76', and 87' create a dependable comeback scenario.
- Lightweight deterministic statistical insights reference precise event IDs; no speculative causation.
- FastAPI delivers a complete, immutable replay JSON response; UI replays it locally.
- Automated tests check seed determinism, score consistency, chronological order, positional bounds, and evidence integrity.

## Next: actual agentic reasoning (not included yet)

1. Detect pressure changes from properly defined possession chains and rolling statistics.
2. Implement Microsoft Agent Framework roles: tactical analyst, narrative director, evidence verifier, audience transformer.
3. Integrate Foundry Local Phi as a configurable inference provider with deterministic/offline fallbacks.
4. Persist auditable agent handoffs, rejections, evidence IDs, and timing.
5. Public Azure Static Web Apps demonstration with precomputed replay and an explicit label distinguishing precomputed from live inference.

## Data licensing

Use only our own synthetic, fictional event data; no EPL branding, copyrighted game footage, or licensed play-by-play is included.
