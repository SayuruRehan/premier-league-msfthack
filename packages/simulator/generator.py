"""Reproducible *fictional* football replay. Not a physics or match prediction engine."""
import random
from .models import MatchEvent, Position

HOME = ("Northbridge FC", ["A. Reed", "J. Moreno", "L. Price", "O. Blake", "N. Harris"])
AWAY = ("Harbor City", ["M. Silva", "D. Costa", "R. Walker", "S. Okafor", "T. Chen"])
DURATION = 90 * 60

def generate_events(seed: int = 7) -> list[MatchEvent]:
    rng = random.Random(seed)
    events: list[MatchEvent] = []
    possession = "home"
    # A fixed, compelling comeback scenario that varies in incidental passes and locations.
    goals = {29 * 60: "home", 76 * 60: "away", 87 * 60: "away"}
    for second in range(30, DURATION + 1, 30):
        if second in goals:
            team = goals[second]
            kind = "goal"
            possession = "away" if team == "home" else "home"
        else:
            # Away side increases its pressure after minute 65.
            away_bias = 0.76 if second >= 65 * 60 else 0.48
            if rng.random() < 0.28:
                kind = "turnover"
                possession = "away" if possession == "home" else "home"
            else:
                kind = rng.choices(["pass", "shot", "tackle"], [0.76, 0.12, 0.12])[0]
                if rng.random() < 0.18:
                    possession = "away" if rng.random() < away_bias else "home"
            team = possession
        players = HOME[1] if team == "home" else AWAY[1]
        x = round(rng.uniform(8, 91), 1)
        y = round(rng.uniform(10, 90), 1)
        destination = Position(x=round(min(100, max(0, x + rng.uniform(-22, 22))), 1), y=round(min(100, max(0, y + rng.uniform(-25, 25))), 1)) if kind == "pass" else None
        player = rng.choice(players)
        successful = kind != "shot" and (kind != "pass" or rng.random() > 0.14)
        events.append(MatchEvent(id=f"evt-{second:04d}", second=second, team=team, kind=kind,
            player=player, position=Position(x=x, y=y), target=destination,
            success=successful, description=f"{player}: {kind.replace('_', ' ')}" + (" (goal!)" if kind == "goal" else "")))
    return events
