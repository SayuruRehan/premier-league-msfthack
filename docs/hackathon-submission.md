# MatchShift AI — Submission copy

> **Status:** Draft copy for the Premier League × Microsoft "Inside the Game" Developer Hackathon. Fill in the final video link and confirm the entrant details in the official submission portal. This Markdown is not a submitted entry.

## Project title

**MatchShift AI — Every Turning Point, Explained**

## One-line pitch

A verified, agent-orchestrated football storytelling engine that transforms synthetic match events into timed broadcast overlays and distinct fan, analyst and broadcaster experiences.

## Project description (ready to adapt for the submission form)

A score tells you what happened. MatchShift AI helps explain **why a match moment matters**.

Our prototype simulates a fictional 90-minute football match and transforms passes, goals, turnovers and recoveries into reproducible five-minute tactical signals. When the system detects a goal or a meaningful high-regain shift, it generates a synchronized broadcast cue with a timeline position, pitch focus, and traceable source event IDs.

Four specialized roles orchestrated with **Microsoft Agent Framework** work together: a Tactical Analyst assembles the evidence, a Narrative Director selects a storytelling angle, an Evidence Verifier checks every claim against the match data, and an Audience Agent adapts the approved narration to fans, analysts or broadcasters. The verifier rejects unsupported decisions and the pipeline recovers through a safe fallback. Two roles can optionally use **Microsoft Foundry Local** with Phi for genuine local model-based decisions, while deterministic operation remains available without an AI subscription.

The interactive **React/TypeScript** match studio is hosted on **Azure Static Web Apps Free**. For reliable public judging, the site serves precomputed, verified Agent Framework outputs: it does **not** imply that a model runs in each visitor's browser. The backend and replay tools use **Python, FastAPI and GitHub Actions**, with automated evidence evaluation and browser tests.

**Impact:** A foundation for editorially safe, scalable fan-personalized match narratives that can be integrated alongside licensed live feeds in a future deployment—without inventing statistics or hiding provenance.

## Category selection

**Primary target:** Best Multi-Agent System.

Why: Four distinct typed Agent Framework workflow stages, evidence-based handoffs, rejection and recovery, with optional two-specialist local Phi decisions. Do not claim four independent generative LLM agents; the current system is a **hybrid workflow**.

**Not our primary claim:** Best Azure Cloud Native Integration. Azure Static Web Apps Free is genuine Azure deployment, but this prototype does not use AKS, Functions, event-driven Azure services, or hosted Azure AI.

## Hero technology and evidence table

| Technology | Real use | Proof |
| --- | --- | --- |
| Microsoft Agent Framework (Python) | Runs four workflow stages, explicit typed outputs, rejection and bounded recovery | `packages/agents/workflow.py`, `tests/test_agents.py` |
| Microsoft Foundry Local / Phi (optional) | Two allowlisted local-model decisions: angle and audience style | `scripts/probe_foundry_local.py`, `docs/foundry-local-validation.md` |
| Azure Static Web Apps Free | Public, anonymous host for the standalone synthetic replay | `https://jolly-bay-020154010.1.azurestaticapps.net`, `.github/workflows/deploy-azure-static.yml` |
| GitHub Actions | CI, browser tests, offline export and post-deploy public verification | `.github/workflows/ci.yml`, `.github/workflows/deploy-azure-static.yml` |
| FastAPI + Pydantic | Typed match replay and live local orchestration endpoints | `services/api/app/main.py`, `packages/simulator/models.py` |
| React + TypeScript | Dynamic cue sheet, replay, story modes, evidence timeline and agent trace | `apps/web/src` |

## Links to paste into the portal

- **Public demo:** https://jolly-bay-020154010.1.azurestaticapps.net
- **Public source code:** https://github.com/SayuruRehan/premier-league-msfthack
- **Video (public YouTube/Vimeo etc.):** [ADD AFTER UPLOADING — must be less than 2 minutes]
- **Testing access:** No sign-in required. Start by clicking a goal/tactical highlight, switch between fan/analyst/broadcast modes and inspect the evidence trail.
- **Privacy/licensing:** Fictional clubs, fictional player names and fully synthetic event data; no unlicensed match footage.

## Judge-facing disclosures — do not omit

- The match scenario is **scripted, fictional and reproducible**; it is not true match tracking or predictive analysis.
- "High regains" is a location-based synthetic proxy, **not** measured PPDA or real pressing intensity.
- The public Azure demo serves **saved deterministic outputs** from actual framework workflow executions. It does **not** serve live Phi inference.
- Running Microsoft Foundry Local and measuring actual inference must be demonstrated separately using real local hardware; do **not** state it was validated unless the probe has passed.
- No licensed Premier League logos, match footage or official competition data are included.

## Submission checklist

- [ ] Registration completed by October 20, 2026, noon Pacific Time.
- [ ] Submit by **October 27, 2026, 11:59 PM Pacific Time** (October 28, 2026, 12:29 PM Sri Lanka).
- [ ] Re-read the competition's current official rules before submitting.
- [ ] Public repository still accessible.
- [ ] Azure demo reachable without sign-in, including complete JSON and all personas.
- [ ] Under-two-minute original video uploaded as **public**, not unlisted if the form expressly requires public.
- [ ] Video demonstrates the actual product on screen and uses only owned/suitably licensed sound and visuals.
- [ ] Optional Foundry Local claims supported by a genuine local probe; otherwise disclose as optional integration only.
- [ ] Enter project pitch, GitHub URL, hosted URL, video URL and correct category on the hackathon portal.
- [ ] Save the confirmation receipt/screenshot. Keep the free judge demo accessible throughout the judging period.
