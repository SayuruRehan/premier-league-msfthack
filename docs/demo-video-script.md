# MatchShift AI — 1:50 video script and shot list

**Target total:** 110 seconds. **Hard limit:** under 120 seconds. The screen recording must show the running project. Use the hosted Azure demo for the whole browser segment; use a local Foundry run only when it is actually available and proven.

| Time | What to show | Natural voiceover |
| --- | --- | --- |
| 0–12s | MatchShift homepage, pitch and controls | “Football isn't just the score. The interesting part is *why* a match turns. MatchShift AI turns raw events into a story fans can actually follow.” |
| 12–26s | Click 29-minute goal in the cue rail | “This is a fully fictional match. Every pass, turnover and goal is simulated, and every moment has a real event ID behind it.” |
| 26–43s | Jump to a late high-regain/tactical cue, show spotlight and five-minute metrics | “Here the side winning the ball higher up the pitch changes its pattern. We calculate the change from the last two five-minute windows; we don't invent an explanation.” |
| 43–60s | Switch from FAN to ANALYST then BROADCAST modes | “The same verified observation becomes three different experiences: a simple fan explanation, the underlying metric for an analyst, and concise broadcast-ready copy.” |
| 60–81s | Scroll to the execution trace: 4 stages | “Microsoft Agent Framework coordinates four roles: analysis, directing, verifying and audience adaptation. A verifier checks the source evidence and rejects unsupported decisions before publication.” |
| 81–96s | Click a source event to seek back, then return to highlight | “Every cue and claim is traceable back to the exact synthetic source event. If an inference provider fails, the workflow safely falls back.” |
| 96–110s | Show the URL and final broadcast canvas; optionally show GitHub | “The public experience runs on Azure Static Web Apps. It's free to explore and uses verified precomputed workflows; local Phi inference is optional. MatchShift: every turning point, explained.” |

## Recording instructions

1. Use a clean 1080p or higher screen capture at a comfortable browser zoom; pause or crop distracting tabs.
2. Open https://jolly-bay-020154010.1.azurestaticapps.net in a private window and refresh. Do a full practice walkthrough before recording.
3. Keep the score, timeline and `SYNTHETIC MATCH REPLAY` label legible throughout.
4. Click the actual highlighted insight near minutes 67–74; exact cue times may vary with the script/seed. Do not describe this as measured tracking-derived pressing.
5. Show the Microsoft workflow trace from the verified story card. Do not edit the video to imply the static site is calling a live LLM.
6. Record original voiceover (or use clearly permitted audio). **Do not use copyrighted sports commentary, match footage, league crests or stadium clips.**
7. Export to MP4 and check the duration is strictly below 120 seconds. Publish the finished recording using a public video URL accepted by the official submission form.
8. Copy the public video URL into `docs/hackathon-submission.md` and the official submission site; submit and retain confirmation.

## Optional on-screen real Phi evidence

Only if `python -m scripts.probe_foundry_local` has genuinely passed on your hardware: you may record the terminal probe and explain that *two* roles choose angle and style through local Phi, while deterministic evidence verification and narration templates prevent invented claims. This is not required for the public judge demo and must never be simulated as a real model session.

## Quick guided tour for the recording

The broadcast canvas now includes **Guided tour · 27s**. It automatically shows a goal in Fan mode, a high-regain shift in Analyst mode, and the late goal in Broadcast mode, using only genuine precomputed cues and verified stories. It uses nine seconds per stop and can be stopped manually. You may record this sequence as a single clean take, then demonstrate the evidence and trace panels separately.

## Optional Trust Lab sequence (stronger evidence for Best Multi-Agent System)

The judge-facing Agent Trust Lab adds three **controlled, clearly labeled simulated model-failure demonstrations** that run through the actual four-stage framework: unsupported claim → rejected + reverified; endpoint outage → transparent fallback; invalid style → template recovery. For a stronger agentic proof, allocate 12–18 seconds of the original 110-second video to show the invented-claim case and its `EvidenceVerifier: rejected` plus follow-up `approved`. Cut the old "click back into source events" section to maintain a runtime strictly under two minutes. **Never claim these were live Phi outputs.**
