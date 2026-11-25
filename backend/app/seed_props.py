"""
Seed upcoming demo NFL games and published props into the configured database.
Usage (from backend/):
    python -m app.seed_props
Or inside Docker:
    docker compose exec app python -m app.seed_props
"""

from datetime import datetime, timedelta, timezone

from app.db import Base, SessionLocal, engine
from app.models import Game, Prop


def _future_utc(days_ahead: int, hour_utc: int, minute: int = 0) -> datetime:
    base = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).replace(
        hour=hour_utc, minute=minute, second=0, microsecond=0
    )
    return base


DEMO_GAMES = [
    {
        "away_team": "BUF",
        "home_team": "KC",
        "kickoff_at": _future_utc(1, 1, 15),  # 8:15 PM ET next day
        "props": [
            ("James Cook", "Rushing Yards", 72.5),
            ("Josh Allen", "Passing Yards", 275.5),
            ("Patrick Mahomes", "Passing Yards", 268.5),
            ("Travis Kelce", "Receiving Yards", 64.5),
        ],
    },
    {
        "away_team": "DAL",
        "home_team": "SF",
        "kickoff_at": _future_utc(3, 18, 0),  # 1:00 PM ET
        "props": [
            ("CeeDee Lamb", "Receiving Yards", 78.5),
            ("Christian McCaffrey", "Rushing Yards", 81.5),
            ("Dak Prescott", "Passing Yards", 252.5),
            ("George Kittle", "TDs", 0.5),
        ],
    },
    {
        "away_team": "BAL",
        "home_team": "TB",
        "kickoff_at": _future_utc(3, 21, 5),  # 4:05 PM ET
        "props": [
            ("Baker Mayfield", "Passing Yards", 246.5),
            ("Derrick Henry", "Rushing Yards", 85.5),
            ("Lamar Jackson", "Passing Yards", 247.5),
            ("Zay Flowers", "Receiving Yards", 58.5),
        ],
    },
    {
        "away_team": "GB",
        "home_team": "PIT",
        "kickoff_at": _future_utc(4, 1, 20),  # 8:20 PM ET
        "props": [
            ("DK Metcalf", "Receiving Yards", 67.5),
            ("Green Bay Packers", "Game Outcome", 3.5),
            ("Jordan Love", "Passing Yards", 241.5),
            ("Kenneth Gainwell", "Rushing Yards", 54.5),
        ],
    },
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        existing_open = (
            db.query(Game)
            .filter(Game.kickoff_at > now, Game.status == "scheduled")
            .count()
        )
        if existing_open > 0:
            print(f"Database already has {existing_open} upcoming scheduled game(s). Skipping seed.")
            return

        created_games = 0
        created_props = 0
        for game_spec in DEMO_GAMES:
            game = Game(
                away_team=game_spec["away_team"],
                home_team=game_spec["home_team"],
                kickoff_at=game_spec["kickoff_at"],
                status="scheduled",
            )
            db.add(game)
            db.flush()
            created_games += 1

            for player_name, stat_category, line in game_spec["props"]:
                db.add(
                    Prop(
                        game_id=game.id,
                        player_name=player_name,
                        stat_category=stat_category,
                        line=line,
                        status="published",
                    )
                )
                created_props += 1

        db.commit()
        print(f"Seeded {created_games} upcoming games and {created_props} published props.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
