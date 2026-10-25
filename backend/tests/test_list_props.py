from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.api.routes import props as props_routes
from app.core.config import AUTH_COOKIE_NAME
from app.core.security import create_access_token
from app.db import Base
from app.main import get_application
from app.models import Game, Prop, User

NOW = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)


def freeze_time(monkeypatch, moment: datetime) -> None:
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return moment.astimezone(tz)

    monkeypatch.setattr(props_routes, "datetime", FrozenDatetime)


@pytest.fixture
def test_db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(test_db_session, monkeypatch):
    freeze_time(monkeypatch, NOW)
    app = get_application()

    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def member_client(client, test_db_session):
    test_db_session.add(
        User(username="ben", email="ben@example.com", hashed_password="password")
    )
    test_db_session.commit()
    client.cookies.set(AUTH_COOKIE_NAME, create_access_token({"sub": "ben"}))
    return client


def add_game(session, away, home, kickoff, **overrides) -> Game:
    game = Game(away_team=away, home_team=home, kickoff_at=kickoff, **overrides)
    session.add(game)
    session.commit()
    return game


def add_prop(session, game, player, category, line, status="published") -> Prop:
    prop = Prop(
        game=game,
        player_name=player,
        stat_category=category,
        line=line,
        status=status,
    )
    session.add(prop)
    session.commit()
    return prop


def test_list_props_requires_login(client):
    res = client.get("/api/props")

    assert res.status_code == 401


def test_list_props_returns_empty_list_when_nothing_is_open(member_client):
    res = member_client.get("/api/props")

    assert res.status_code == 200
    assert res.json() == []


def test_list_props_matches_frontend_shape(member_client, test_db_session):
    # 4:25 PM and 8:20 PM Eastern on 10/24 (the second is already 10/25 in UTC)
    buf_kc = add_game(
        test_db_session,
        "BUF",
        "KC",
        datetime(2026, 10, 24, 20, 25, tzinfo=timezone.utc),
    )
    dal_sf = add_game(
        test_db_session, "DAL", "SF", datetime(2026, 10, 25, 0, 20, tzinfo=timezone.utc)
    )
    # 12:00 PM Eastern on 10/25
    bal_tb = add_game(
        test_db_session, "BAL", "TB", datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc)
    )
    allen = add_prop(test_db_session, buf_kc, "Josh Allen", "Passing Yards", 275.5)
    cook = add_prop(test_db_session, buf_kc, "James Cook", "Rushing Yards", 72.5)
    kittle = add_prop(test_db_session, dal_sf, "George Kittle", "TDs", 0.5)
    ravens = add_prop(test_db_session, bal_tb, "Baltimore Ravens", "Game Outcome", 3.5)

    res = member_client.get("/api/props")

    assert res.status_code == 200
    assert res.json() == [
        {
            "date": "10/24/2026",
            "games": [
                {
                    "id": str(buf_kc.id),
                    "matchup": "BUF @ KC",
                    "kickoff": "2026-10-24T16:25:00-04:00",
                    "props": [
                        {
                            "id": str(cook.id),
                            "player": "James Cook",
                            "category": "Rushing Yards",
                            "line": "72.5",
                            "matchup": "BUF @ KC",
                            "time": "4:25 PM",
                        },
                        {
                            "id": str(allen.id),
                            "player": "Josh Allen",
                            "category": "Passing Yards",
                            "line": "275.5",
                            "matchup": "BUF @ KC",
                            "time": "4:25 PM",
                        },
                    ],
                },
                {
                    "id": str(dal_sf.id),
                    "matchup": "DAL @ SF",
                    "kickoff": "2026-10-24T20:20:00-04:00",
                    "props": [
                        {
                            "id": str(kittle.id),
                            "player": "George Kittle",
                            "category": "TDs",
                            "line": "0.5",
                            "matchup": "DAL @ SF",
                            "time": "8:20 PM",
                        },
                    ],
                },
            ],
        },
        {
            "date": "10/25/2026",
            "games": [
                {
                    "id": str(bal_tb.id),
                    "matchup": "BAL @ TB",
                    "kickoff": "2026-10-25T12:00:00-04:00",
                    "props": [
                        {
                            "id": str(ravens.id),
                            "player": "Baltimore Ravens",
                            "category": "Game Outcome",
                            "line": "3.5",
                            "matchup": "BAL @ TB",
                            "time": "12:00 PM",
                        },
                    ],
                },
            ],
        },
    ]


def test_list_props_uses_standard_time_after_dst_ends(
    member_client, test_db_session, monkeypatch
):
    freeze_time(monkeypatch, datetime(2026, 10, 31, tzinfo=timezone.utc))
    game = add_game(
        test_db_session, "GB", "PIT", datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    )
    add_prop(test_db_session, game, "DK Metcalf", "Receiving Yards", 67.5)

    body = member_client.get("/api/props").json()

    assert body[0]["date"] == "11/02/2026"
    assert body[0]["games"][0]["kickoff"] == "2026-11-02T13:00:00-05:00"
    assert body[0]["games"][0]["props"][0]["time"] == "1:00 PM"


def test_list_props_only_includes_props_open_within_the_next_week(
    member_client, test_db_session
):
    open_game = add_game(test_db_session, "BUF", "KC", NOW + timedelta(days=1))
    edge_game = add_game(test_db_session, "NE", "NYJ", NOW + timedelta(days=7))
    started_game = add_game(test_db_session, "DAL", "SF", NOW - timedelta(minutes=1))
    far_game = add_game(
        test_db_session, "BAL", "TB", NOW + timedelta(days=7, seconds=1)
    )
    postponed_game = add_game(
        test_db_session, "GB", "PIT", NOW + timedelta(days=2), status="postponed"
    )

    open_prop = add_prop(
        test_db_session, open_game, "Josh Allen", "Passing Yards", 275.5
    )
    edge_prop = add_prop(
        test_db_session, edge_game, "Breece Hall", "Rushing Yards", 60.5
    )
    for status in ["draft", "locked", "settled", "cancelled"]:
        add_prop(test_db_session, open_game, status, "Rushing Yards", 50.5, status)
    add_prop(test_db_session, started_game, "Dak Prescott", "Passing Yards", 252.5)
    add_prop(test_db_session, far_game, "Lamar Jackson", "Passing Yards", 247.5)
    add_prop(test_db_session, postponed_game, "Jordan Love", "Passing Yards", 240.5)

    body = member_client.get("/api/props").json()

    listed_ids = [
        prop["id"]
        for date_group in body
        for game in date_group["games"]
        for prop in game["props"]
    ]
    assert listed_ids == [str(open_prop.id), str(edge_prop.id)]
