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

## Milestone 3: Microsoft Agent Framework workflow (implemented)

- Actual Microsoft `@workflow` orchestration with four typed `@step` roles (TacticalAnalyst, NarrativeDirector, EvidenceVerifier, AudienceAgent).
- Default zero-cost deterministic stories; optional local Phi model selects a strictly validated narrative framing.
- Claim/evidence verification, bounded rejection-and-retry recovery, explicit model fallback provenance.
- Fan, analyst and broadcaster narration modes with a visible execution trace.
- Reference: `docs/agents.md`.

## Next: deeper AI and showcase (not implemented yet)

1. Expand the local model to multiple genuinely generative specialist roles with claim validation, evaluation and latency budgets.
2. Add persistent workflow run logs, latency metrics and observable real-time handoffs.
3. Build a polished broadcast overlay and a short high-impact demonstration.
4. Deploy a zero-cost public Azure Static Web Apps experience with disclosed precomputed inference and, if available, optional live model inference.

## Data licensing

Use only our own synthetic, fictional event data; no EPL branding, copyrighted game footage, or licensed play-by-play is included.
