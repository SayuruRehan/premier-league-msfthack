# Hackathon judging evidence and scope audit

Official rules: https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md

This document aligns honest engineering proof to the hackathon's five equally weighted (20% each) judging criteria. It is an audit guide, **not a predicted score**.

| Criterion (20% each) | Implemented proof | Remaining weakness / action |
| --- | --- | --- |
| Technological implementation | Typed Pydantic event/insight contracts, deterministic simulation, FastAPI endpoints, Azure Static Web Apps Free, CI, Playwright and public anonymous smoke tests | Add documented performance and proper fixture realism assessment; avoid implying real match analytics accuracy |
| Agentic design and innovation | `packages/agents/workflow.py`: real Microsoft Agent Framework `@workflow`, four typed roles, evidence revalidation, bounded retry and model failure fallback | Two optionally model-backed roles currently select **tokens**, not freeform content; exercise real Phi on compatible hardware to strengthen credibility |
| Real-world applicability | Timed, machine-readable `BroadcastCue` objects with evidence IDs, synthetic fan/analyst/broadcast narratives, no network required for public judge demo | Production would require licensed data feeds, ingestion scaling, rights management, a hosted secure inference deployment and latency work |
| UX / presentation | Broadcast pitch overlay, cue timeline and spotlight, audience modes, clickable evidence, focus view, desktop/mobile Playwright tests | Record a polished original video strictly under two minutes; visual review with multiple device sizes |
| Category alignment: Best Multi-Agent System | Tactical Analyst → Narrative Director → Evidence Verifier → Audience Agent with typed handoffs; model exceptions and invalid outputs handled deterministically | Clearly show WHY the stages collaborate; do not claim four independent LLM services |

## Category strategy

**Best Multi-Agent System** is the most defensible category: genuine Microsoft Agent Framework workflow and agent trace with human-interpretable accountability.

Azure Static Web Apps is a legitimate hero technology for hosting, but there are no Azure Functions, Event Hubs or other cloud-native compute components in this version, so don't present it as a fully Azure-native distributed agent platform.

## Evidence availability

- **Public demo:** https://jolly-bay-020154010.1.azurestaticapps.net
- **Repo:** https://github.com/SayuruRehan/premier-league-msfthack
- **Tests:** `tests/`, `apps/web/e2e/`, and `.github/workflows/ci.yml`
- **Evaluation:** `python -m scripts.evaluate` writes measured results to `artifacts/evaluation/`; CI artifacts provide the report for reviewers.
- **Real Phi proof:** `python -m scripts.probe_foundry_local` must pass on actual hardware before claiming validation.
- **Submission:** `docs/hackathon-submission.md` and `docs/demo-video-script.md`.

## Risks to resolve before submission

1. Stronger narrative differentiation between fan, analyst and broadcaster beyond formatting.
2. Confirm optional Foundry Local model compatibility with the actual host machine.
3. Capture an original, compelling under-two-minute video, and test the public link in an incognito browser.
4. Preserve Azure Free tier and maintain the public URL through the judging period.
5. Ensure synthetic scenario and generated outputs are not described as live licensed match analysis.

## Public failure-recovery demonstration (Milestone 8)

The production build now exports `trust_lab.json` with **three explicitly simulated provider responses** and their **real Agent Framework execution traces**. Judges can inspect verifier rejection, bounded re-check, fallback on model unavailability, and audience-style validation, with final copy remaining grounded in exact match evidence. The scenarios are developer-controlled tests, **not live Phi calls or empirically observed production incidents**.
