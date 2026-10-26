from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import events
from app.db import Base
from app.models import Game, Prop

KICKOFF = datetime(2026, 10, 24, 20, 25, tzinfo=timezone.utc)


# Creates temp database for testing
@pytest.fixture
def database_engine():
    engine = create_engine("sqlite:///:memory:")

    # SQLite only enforces foreign keys when asked to
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_game(**overrides) -> Game:
    game_data = {
        "away_team": "BUF",
        "home_team": "KC",
        "kickoff_at": KICKOFF,
    }
    game_data.update(overrides)
    return Game(**game_data)


def make_prop(game: Game, **overrides) -> Prop:
    prop_data = {
        "game": game,
        "player_name": "Josh Allen",
        "stat_category": "Passing Yards",
        "line": 275.5,
    }
    prop_data.update(overrides)
    return Prop(**prop_data)


def test_startup_creates_games_and_props_tables(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(events, "engine", engine)

    events.create_start_app_handler(None)()

    table_names = inspect(engine).get_table_names()
    assert {"users", "games", "props"} <= set(table_names)
    engine.dispose()


def test_game_and_prop_schemas_have_named_constraints():
    game_constraints = {c.name for c in Game.__table__.constraints}
    prop_constraints = {c.name for c in Prop.__table__.constraints}

    assert {
        "uq_games_matchup_kickoff",
        "ck_games_distinct_teams",
        "ck_games_status",
    } <= game_constraints
    assert {
        "uq_props_game_player_category",
        "ck_props_stat_category",
        "ck_props_status",
        "ck_props_line_half_increment",
        "fk_props_game_id",
    } <= prop_constraints


def test_new_game_and_prop_receive_defaults(database_engine):
    game = make_game()
    prop = make_prop(game)

    with Session(database_engine) as session:
        session.add(prop)
        session.commit()
        session.refresh(game)
        session.refresh(prop)

        assert game.status == "scheduled"
        assert game.created_at is not None
        assert prop.status == "draft"
        assert prop.created_at is not None
        assert prop.game_id == game.id
        assert game.props == [prop]


def test_game_matchup_matches_frontend_format():
    assert make_game().matchup == "BUF @ KC"


def test_game_kickoff_round_trips(database_engine):
    with Session(database_engine) as session:
        session.add(make_game())
        session.commit()

        stored = session.query(Game).one()
        # SQLite drops tzinfo; Postgres keeps it. Compare the wall-clock UTC value.
        assert stored.kickoff_at.replace(tzinfo=timezone.utc) == KICKOFF


@pytest.mark.parametrize("required_field", ["away_team", "home_team", "kickoff_at"])
def test_required_game_fields_cannot_be_null(database_engine, required_field):
    game = make_game(**{required_field: None})

    with Session(database_engine) as session:
        session.add(game)
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize("required_field", ["player_name", "stat_category", "line"])
def test_required_prop_fields_cannot_be_null(database_engine, required_field):
    prop = make_prop(make_game(), **{required_field: None})

    with Session(database_engine) as session:
        session.add(prop)
        with pytest.raises(IntegrityError):
            session.commit()


def test_prop_must_belong_to_a_game(database_engine):
    prop = make_prop(None)

    with Session(database_engine) as session:
        session.add(prop)
        with pytest.raises(IntegrityError):
            session.commit()


def test_prop_must_reference_existing_game(database_engine):
    prop = make_prop(None, game_id=999)

    with Session(database_engine) as session:
        session.add(prop)
        with pytest.raises(IntegrityError):
            session.commit()


def test_game_rejects_same_team_on_both_sides(database_engine):
    with Session(database_engine) as session:
        session.add(make_game(home_team="BUF"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_game_rejects_invalid_status(database_engine):
    with Session(database_engine) as session:
        session.add(make_game(status="halftime"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_duplicate_game_is_rejected_but_rematch_is_allowed(database_engine):
    with Session(database_engine) as session:
        session.add(make_game())
        session.add(make_game(kickoff_at=KICKOFF + timedelta(days=90)))
        session.commit()

        session.add(make_game())
        with pytest.raises(IntegrityError):
            session.commit()


def test_duplicate_prop_for_same_game_is_rejected(database_engine):
    game = make_game()

    with Session(database_engine) as session:
        session.add(make_prop(game))
        session.commit()

        session.add(make_prop(game, line=280.5))
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize(
    "category",
    ["Game Outcome", "Passing Yards", "Rushing Yards", "Receiving Yards", "TDs"],
)
def test_prop_accepts_frontend_categories(database_engine, category):
    with Session(database_engine) as session:
        session.add(make_prop(make_game(), stat_category=category))
        session.commit()


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [("stat_category", "Sacks"), ("stat_category", "All"), ("status", "open")],
)
def test_prop_rejects_invalid_category_and_status(
    database_engine, field, invalid_value
):
    with Session(database_engine) as session:
        session.add(make_prop(make_game(), **{field: invalid_value}))
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize("line", [0.5, 3.5, 72.5, 299.5])
def test_prop_accepts_half_point_lines(database_engine, line):
    with Session(database_engine) as session:
        session.add(make_prop(make_game(), line=line))
        session.commit()


@pytest.mark.parametrize("line", [300, 299.0, 299.25, 299.4, 0, -3.5])
def test_prop_rejects_lines_that_could_tie_or_are_not_positive(database_engine, line):
    with Session(database_engine) as session:
        session.add(make_prop(make_game(), line=line))
        with pytest.raises(IntegrityError):
            session.commit()
