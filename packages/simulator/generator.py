"""Deterministic *fictional* match simulator, not a football physics model.

All action ownership is explicit. Goals and a short high-press phase are scripted
to make the demonstration reproducible. Incidental play varies with the seed.
"""
import random
from .models import MatchEvent, Position

HOME = ("Northbridge FC", ["A. Reed", "J. Moreno", "L. Price", "O. Blake", "N. Harris"])
AWAY = ("Harbor City", ["M. Silva", "D. Costa", "R. Walker", "S. Okafor", "T. Chen"])
DURATION = 90 * 60
GOALS = {29 * 60: "home", 76 * 60: "away", 87 * 60: "away"}
# A coordinated demonstration phase: home plays out, away wins it high.
PRESS_MINUTES = set(range(67, 73))

def opponent(team: str) -> str:
    return "away" if team == "home" else "home"

def clamp(value: float) -> float:
    return round(max(0, min(100, value)), 1)

def generate_events(seed: int = 7) -> list[MatchEvent]:
    rng = random.Random(seed)
    events: list[MatchEvent] = []
    possession = "home"
    previous: MatchEvent | None = None
    chain_no = 0

    for second in range(30, DURATION + 1, 30):
        scorer = GOALS.get(second)
        pregoal = GOALS.get(second + 30)
        press_recovery = second % 60 == 0 and second // 60 in PRESS_MINUTES
        press_setup = second % 60 == 30 and (second + 30) // 60 in PRESS_MINUTES

        team = possession
        if scorer is not None:
            team, kind, success = scorer, "goal", True
        elif pregoal is not None:
            team = pregoal
            kind = "turnover" if team != possession else "pass"
            success = True
        elif press_recovery:
            team, kind, success = "away", "turnover", True
        elif press_setup:
            team = "home"
            kind = "turnover" if possession != "home" else "pass"
            success = True
        else:
            # An away press increases the home side's chance of losing possession.
            regain_probability = 0.16 if second < 65 * 60 else (0.46 if possession == "home" else 0.09)
            if rng.random() < regain_probability:
                team = opponent(possession)
                kind = "tackle" if rng.random() < 0.25 else "turnover"
                success = True
            else:
                kind = "shot" if rng.random() < 0.10 else "pass"
                success = kind == "pass" and rng.random() >= 0.10

        # Defensive regains are owned by the team winning the ball.
        new_chain = previous is None or team != previous.team or kind in ("turnover", "tackle") or previous.kind in ("goal", "shot") or not previous.success
        if new_chain:
            chain_no += 1
        possession_id = f"pos-{chain_no:03d}"

        if kind in ("turnover", "tackle"):
            if team == "away" and second >= 65 * 60:
                x = rng.uniform(13, 34)  # away winning it near home's goal
            elif team == "home" and second >= 65 * 60:
                x = rng.uniform(58, 85)
            else:
                x = rng.uniform(39, 75)
            y = rng.uniform(15, 85)
        elif kind in ("goal", "shot"):
            x = rng.uniform(80, 93) if team == "home" else rng.uniform(7, 20)
            y = rng.uniform(28, 72)
        elif previous and previous.team == team and previous.target is not None and previous.success and previous.kind == "pass":
            x, y = previous.target.x, previous.target.y
        else:
            x = rng.uniform(30, 70)
            y = rng.uniform(18, 82)

        position = Position(x=clamp(x), y=clamp(y))
        target = None
        if kind == "pass":
            direction = 1 if team == "home" else -1
            target = Position(x=clamp(x + direction * rng.uniform(2, 17)), y=clamp(y + rng.uniform(-18, 18)))
        player = rng.choice(HOME[1] if team == "home" else AWAY[1])
        event = MatchEvent(
            id=f"evt-{second:04d}", second=second, team=team, kind=kind,
            player=player, position=position, target=target, success=success,
            possession_id=possession_id,
            description=f"{player}: {kind}" + (" (goal!)" if kind == "goal" else (" (intercepted)" if kind == "pass" and not success else "")),
        )
        events.append(event)
        previous = event
        possession = opponent(team) if kind in ("goal", "shot") or (kind == "pass" and not success) else team

    return events
