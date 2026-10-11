# MatchShift AI — Hackathon demo runbook

## Objective

Show the **value of a trustworthy multi-agent match broadcast** within the hackathon's under-two-minute video limit, without overclaiming autonomy or implying the synthetic replay is licensed match data.

## Prerequisites

- Start FastAPI: `pip install -r services/api/requirements.txt && uvicorn services.api.app.main:app --reload`.
- Start React: `cd apps/web && npm install && npm run dev`.
- Default mode is **free and deterministic**, powered by Microsoft Agent Framework orchestration. Optional real inference can be enabled only when a compatible Foundry Local Phi model is installed.
- Verify `GET /api/agents/config` shows the expected provider.
- Set the browser to 1080p or higher and zoom if necessary; turn on browser focus mode.
- Do not use external Premier League footage, imagery, team crests or official play-by-play data.

## Suggested 110-second video sequence

| Duration | On-screen action | What we demonstrate |
| --- | --- | --- |
| 0–12s | Explain the product with the broadcast canvas | "Every turning point, explained and verified" |
| 12–28s | Jump to the first scored goal at 29:00 | Cue appears with scoreboard, time and field focus |
| 28–52s | Navigate to a tactical-shift cue around minutes 67–74 | Five-minute regain evidence, highlighted pitch area |
| 52–73s | Toggle fan / analyst / broadcast audience modes | Same sourced event, different safe audience presentation |
| 73–90s | Show the Microsoft Agent Framework execution trace | Tactical Analyst → Narrative Director → Evidence Verifier → Audience Agent |
| 90–104s | Click into source evidence and show rejection/fallback handling in a local test or narrated explanation | Traceability and hallucination control |
| 104–110s | Close on the broadcaster canvas | Microsoft Agent Framework + optional Foundry Local Phi |

## What to say accurately

- Four real workflow stages are executed with typed agent handoffs via Microsoft Agent Framework.
- Only the Director and the Audience Style stage are *optionally* model-backed; the default is deterministic.
- Numerical claims are recomputed from synthetic events and are not authored by an LLM.
- On-screen overlays are **timed replay cues** based on the source event data, not real camera/video tracking.
- If model inference is not actually running, say "Foundry Local integration available" rather than "powered by Phi right now."

## Before public release

- Validate browser playback and on-air card visibility on mobile and desktop.
- Test no network/temporary inference failure while keeping cue playback functioning.
- Publish a stable publicly accessible URL; ensure judges do not need to authenticate or run a local API.
- Add a disclaimer: fictional players, teams and match events. No licensed footage.
- Capture a video at least one day before the submission deadline.
