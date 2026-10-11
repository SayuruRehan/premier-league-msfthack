# MatchShift Architecture and Roadmap

## Foundation (merged)

- Event contract: Pydantic MatchEvent with normalized location (0–100 on each axis).
- 90-minute simulated replay of fictional Northbridge FC vs Harbor City, seeded for reproducibility.
- Scripted goals at 29', 76', and 87' create a dependable comeback scenario.
- Lightweight deterministic statistical insights reference precise event IDs; no speculative causation.
- FastAPI delivers a complete, immutable replay JSON response; UI replays it locally.
- Automated tests check seed determinism, score consistency, chronological order, positional bounds, and evidence integrity.

## Milestone 2: rolling football analytics

- Explicit possession IDs and ball-winning events with team ownership.
- Deterministic 5-minute metrics with non-overlapping windows for tactical-shift comparison.
- Location-based high regain proxy with cooldown and evidence IDs spanning both comparison windows.
- UI metric panel with click-through to underlying match events.
- Documentation: `docs/analytics.md`.

## Next: actual agentic reasoning (not included yet)

1. Implement Microsoft Agent Framework roles: tactical analyst, narrative director, evidence verifier, audience transformer.
2. Integrate Foundry Local Phi as a configurable inference provider with deterministic/offline fallbacks.
3. Persist auditable agent handoffs, rejections, evidence IDs, and timing.
4. Public Azure Static Web Apps demonstration with precomputed replay and explicit disclosure of live versus cached inference.

## Data licensing

Use only our own synthetic, fictional event data; no EPL branding, copyrighted game footage, or licensed play-by-play is included.
