# Synthetic match analytics — definitions and limitations

This project uses a seeded, **fictional** match. Our goal is interpretable metrics and evidence-linked narratives, not real-world football analytics accuracy.

## Event semantics
- `team` is the actor. A `turnover` or `tackle` is recorded against the team **winning** possession.
- A successful pass continues possession; an unsuccessful pass ends possession. A shot or goal ends the possession even when the next event is in the same team.
- `possession_id` identifies consecutive actions of one possession; there is no opponent possession contamination.
- Events happen every 30 seconds. There is no inference of possession duration from events, so "possession share" is intentionally not provided.
- The demo includes scripted goals (29', 76', 87') and away high ball regains from 67'–72'. All other actions are seeded, synthetic pseudorandom events.

## Five-minute rolling metrics
At each 60-second checkpoint `t`, only events satisfying `t-300 < event.second <= t` are considered. The time windows used for tactical shifts are *non-overlapping*: current `(t-300, t]`, preceding `(t-600, t-300]`.

- **Regains** = successful turnovers + successful tackles, as defined in our simulation.
- **High regains** = home regains at `x >= 60`, away regains at `x <= 40` (home attacks toward x=100; away toward x=0). This is an explicit location-based approximation. Do **not** describe it as measured PPDA or actual pressing.
- **Pass completion** = successful passes / all passes in that time window; `null` means no pass attempts, not zero percent.
- **Shots** = unsuccessful shot attempts + goals.
- **Goals** = successful goal events.

## Tactical detection
A tactical-shift insight is raised when one team has at least 3 high regains in the last five minutes, with at least 3 more than the previous five-minute window. Enforce a per-team 10-minute cooldown.

Each shift insight references **all event IDs in both comparison windows**, including those that did not become regains. This makes the absence or presence of regains independently verifiable and prevents the model from claiming unsourced causation.

## Honest limitations / next milestone
- The tactical narrative is deterministic, not an LLM inference.
- There is no player tracking, match footage, true possessions measured by time, off-ball pressing, or xG.
- Microsoft Agent Framework + Foundry Local integration follows after this fully testable data foundation.
