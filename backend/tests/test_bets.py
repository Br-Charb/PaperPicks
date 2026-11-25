from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
from app.db import Base
from app.main import get_application
from app.models import Bet, BetLeg, Game, Prop, User
from app.schemas.bet import BetCreate, BetLegCreate
from app.services import betting as betting_service


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
def client(test_db_session):
    app = get_application()

    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_user(
    db: Session,
    username: str = "bettor1",
    email: str = "bettor1@example.com",
    balance: int = 10000,
    account_status: str = "active",
) -> tuple[User, dict[str, str]]:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("password123"),
        balance=balance,
        account_status=account_status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username, "role": user.role})
    return user, {"Authorization": f"Bearer {token}"}


def _create_prop(
    db: Session,
    player_name: str = "Josh Allen",
    stat_category: str = "Passing Yards",
    line: float = 275.5,
    prop_status: str = "published",
    game_status: str = "scheduled",
    kickoff_offset_hours: int = 24,
) -> Prop:
    game = Game(
        away_team="BUF",
        home_team="KC",
        kickoff_at=datetime.now(timezone.utc) + timedelta(hours=kickoff_offset_hours),
        status=game_status,
    )
    prop = Prop(
        game=game,
        player_name=player_name,
        stat_category=stat_category,
        line=line,
        status=prop_status,
    )
    db.add_all([game, prop])
    db.commit()
    db.refresh(prop)
    return prop


def test_bet_routes_require_auth(client):
    assert client.post("/api/bets", json={"wager": 100, "legs": [{"prop_id": 1, "pick": "over"}]}).status_code == 401
    assert client.get("/api/bets").status_code == 401


def test_place_bet_multi_leg_deducts_balance_and_calculates_payout(client, test_db_session):
    user, headers = _create_user(test_db_session, balance=1000)
    prop1 = _create_prop(test_db_session, player_name="Josh Allen", line=275.5)
    prop2 = _create_prop(test_db_session, player_name="Travis Kelce", stat_category="Receiving Yards", line=64.5)

    res = client.post(
        "/api/bets",
        headers=headers,
        json={
            "wager": 250,
            "legs": [
                {"prop_id": prop1.id, "pick": "over"},
                {"prop_id": prop2.id, "pick": "under"},
            ],
        },
    )

    assert res.status_code == 201
    data = res.json()
    assert data["balance"] == 750
    bet = data["bet"]
    assert bet["wager"] == 250
    assert bet["multiplier"] == 2.0
    assert bet["potential_payout"] == 500
    assert bet["actual_payout"] == 0
    assert bet["status"] == "pending"
    assert len(bet["legs"]) == 2
    assert bet["legs"][0]["player_name"] == "Josh Allen"
    assert bet["legs"][0]["line_snapshot"] == 275.5
    assert bet["legs"][0]["matchup"] == "BUF @ KC"

    test_db_session.refresh(user)
    assert user.balance == 750


def test_place_bet_rejects_insufficient_balance_atomically(client, test_db_session):
    user, headers = _create_user(test_db_session, balance=100)
    prop = _create_prop(test_db_session)

    res = client.post(
        "/api/bets",
        headers=headers,
        json={"wager": 150, "legs": [{"prop_id": prop.id, "pick": "over"}]},
    )

    assert res.status_code == 400
    assert "Insufficient" in res.json()["detail"]

    test_db_session.refresh(user)
    assert user.balance == 100
    assert test_db_session.query(Bet).count() == 0
    assert test_db_session.query(BetLeg).count() == 0


def test_place_bet_rejects_duplicate_prop_in_slip(client, test_db_session):
    user, headers = _create_user(test_db_session, balance=500)
    prop = _create_prop(test_db_session)

    res = client.post(
        "/api/bets",
        headers=headers,
        json={
            "wager": 100,
            "legs": [
                {"prop_id": prop.id, "pick": "over"},
                {"prop_id": prop.id, "pick": "under"},
            ],
        },
    )

    assert res.status_code == 400
    assert "Duplicate" in res.json()["detail"]
    test_db_session.refresh(user)
    assert user.balance == 500
    assert test_db_session.query(Bet).count() == 0


def test_place_bet_rejects_missing_or_closed_prop(client, test_db_session):
    user, headers = _create_user(test_db_session, balance=500)
    draft_prop = _create_prop(test_db_session, prop_status="draft")
    started_prop = _create_prop(test_db_session, kickoff_offset_hours=-1)

    missing_res = client.post(
        "/api/bets",
        headers=headers,
        json={"wager": 50, "legs": [{"prop_id": 9999, "pick": "over"}]},
    )
    assert missing_res.status_code == 404

    draft_res = client.post(
        "/api/bets",
        headers=headers,
        json={"wager": 50, "legs": [{"prop_id": draft_prop.id, "pick": "over"}]},
    )
    assert draft_res.status_code == 400

    started_res = client.post(
        "/api/bets",
        headers=headers,
        json={"wager": 50, "legs": [{"prop_id": started_prop.id, "pick": "over"}]},
    )
    assert started_res.status_code == 400

    test_db_session.refresh(user)
    assert user.balance == 500
    assert test_db_session.query(Bet).count() == 0


def test_list_user_bets_returns_only_own_history_newest_first(client, test_db_session):
    user1, headers1 = _create_user(test_db_session, username="u1", email="u1@example.com", balance=1000)
    user2, _ = _create_user(test_db_session, username="u2", email="u2@example.com", balance=1000)
    prop = _create_prop(test_db_session)

    first_bet, _ = betting_service.place_bet(
        test_db_session,
        user1,
        BetCreate(wager=50, legs=[BetLegCreate(prop_id=prop.id, pick="over")]),
    )
    second_bet, _ = betting_service.place_bet(
        test_db_session,
        user1,
        BetCreate(wager=75, legs=[BetLegCreate(prop_id=prop.id, pick="under")]),
    )
    betting_service.place_bet(
        test_db_session,
        user2,
        BetCreate(wager=100, legs=[BetLegCreate(prop_id=prop.id, pick="over")]),
    )

    res = client.get("/api/bets", headers=headers1)
    assert res.status_code == 200
    history = res.json()
    assert len(history) == 2
    assert [b["id"] for b in history] == [second_bet.id, first_bet.id]
    assert history[0]["wager"] == 75
    assert history[1]["wager"] == 50

    filtered = client.get("/api/bets?status=won", headers=headers1)
    assert filtered.status_code == 200
    assert filtered.json() == []
