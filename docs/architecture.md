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

## Milestone 4: broadcast director (implemented)

- Broadcast cue sheet with deterministic on-air windows, focus coordinates, metric labels and source-event references.
- Cinematic SVG stadium replay with a clock/score bug, pass traces, pitch spotlight, goal/tactical lower thirds and quick-jump highlight navigation.
- Browser-based focus view for the judging video and a director's cue sheet.
- Second optional local model-backed specialist selects only an audience presentation style. The final narration remains evidence-bound and template-rendered.
- All persona and local-model provenance shown in the multi-agent control room.
- Runbook for the hackathon video: `docs/demo-runbook.md`.

## Next: deployment and submission preparation

1. Validate actual Foundry Local/Phi inference on a supported machine, recording model identifier and run latency.
2. Produce a genuinely public, durable judge-accessible demo on Azure Static Web Apps (with an honest, no-model prerecorded fallback).
3. Add end-to-end browser tests and run accessibility checks on the broadcast view.
4. Create a reproducible two-minute demonstration video, judging writeup and submission checklist.
5. Add persistent workflow run logs and timing/evaluation evidence if time permits.

## Data licensing

Use only our own synthetic, fictional event data; no EPL branding, copyrighted game footage, or licensed play-by-play is included.
