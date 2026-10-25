from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Game, Prop

KICKOFF = datetime(2026, 10, 24, 20, 25, tzinfo=timezone.utc)


# Creates temp database for testing
@pytest.fixture
def database_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_prop(prop_status="published", game_status="scheduled") -> Prop:
    game = Game(away_team="BUF", home_team="KC", kickoff_at=KICKOFF, status=game_status)
    return Prop(
        game=game,
        player_name="Josh Allen",
        stat_category="Passing Yards",
        line=275.5,
        status=prop_status,
    )


def test_published_prop_is_open_before_kickoff():
    prop = make_prop()

    assert prop.is_open_for_picks(KICKOFF - timedelta(seconds=1))


@pytest.mark.parametrize("delta", [timedelta(0), timedelta(minutes=1)])
def test_prop_locks_at_kickoff(delta):
    prop = make_prop()

    assert not prop.is_open_for_picks(KICKOFF + delta)


@pytest.mark.parametrize("prop_status", ["draft", "locked", "settled", "cancelled"])
def test_unpublished_prop_is_not_open(prop_status):
    prop = make_prop(prop_status=prop_status)

    assert not prop.is_open_for_picks(KICKOFF - timedelta(days=1))


@pytest.mark.parametrize(
    "game_status", ["in_progress", "final", "postponed", "cancelled"]
)
def test_prop_on_unscheduled_game_is_not_open(game_status):
    prop = make_prop(game_status=game_status)

    assert not prop.is_open_for_picks(KICKOFF - timedelta(days=1))


def test_is_open_for_picks_defaults_to_current_time():
    assert not make_prop().is_open_for_picks()  # KICKOFF is in the past

    prop = make_prop()
    prop.game.kickoff_at = datetime.now(timezone.utc) + timedelta(hours=1)
    assert prop.is_open_for_picks()


def test_kickoff_with_offset_is_stored_as_utc(database_engine):
    eastern = timezone(timedelta(hours=-4))
    kickoff = datetime(2026, 10, 24, 16, 25, tzinfo=eastern)

    with Session(database_engine) as session:
        session.add(Game(away_team="BUF", home_team="KC", kickoff_at=kickoff))
        session.commit()
        session.expire_all()

        stored = session.query(Game).one()
        assert stored.kickoff_at.replace(tzinfo=timezone.utc) == kickoff
        assert stored.has_kicked_off(kickoff)
        assert not stored.has_kicked_off(kickoff - timedelta(seconds=1))
