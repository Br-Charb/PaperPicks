from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.config import AUTH_COOKIE_NAME
from app.core.security import create_access_token
from app.db import Base
from app.main import get_application
from app.models import Game, Prop, User


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


def login_as(client, session, role: str) -> None:
    session.add(
        User(
            username=role,
            email=f"{role}@example.com",
            hashed_password="password",
            role=role,
        )
    )
    session.commit()
    client.cookies.set(AUTH_COOKIE_NAME, create_access_token({"sub": role}))


@pytest.fixture
def admin_client(client, test_db_session):
    login_as(client, test_db_session, "admin")
    return client


def add_game(session, kickoff_delta=timedelta(days=3), **overrides) -> Game:
    game_data = {
        "away_team": "BUF",
        "home_team": "KC",
        "kickoff_at": datetime.now(timezone.utc) + kickoff_delta,
    }
    game_data.update(overrides)
    game = Game(**game_data)
    session.add(game)
    session.commit()
    return game


def add_prop(session, game: Game, **overrides) -> Prop:
    prop_data = {
        "game_id": game.id,
        "player_name": "Josh Allen",
        "stat_category": "Passing Yards",
        "line": 275.5,
    }
    prop_data.update(overrides)
    prop = Prop(**prop_data)
    session.add(prop)
    session.commit()
    return prop


def prop_payload(game_id: int, **overrides) -> dict:
    payload = {
        "game_id": game_id,
        "player_name": "Josh Allen",
        "stat_category": "Passing Yards",
        "line": 275.5,
    }
    payload.update(overrides)
    return payload


def test_admin_can_create_prop_as_draft(admin_client, test_db_session):
    game = add_game(test_db_session)

    res = admin_client.post("/api/admin/props", json=prop_payload(game.id))

    assert res.status_code == 201
    body = res.json()
    assert body["game_id"] == game.id
    assert body["player_name"] == "Josh Allen"
    assert body["stat_category"] == "Passing Yards"
    assert body["line"] == 275.5
    assert body["status"] == "draft"
    assert test_db_session.query(Prop).count() == 1


def test_create_prop_rejects_bad_line_with_clear_message(admin_client, test_db_session):
    game = add_game(test_db_session)

    res = admin_client.post("/api/admin/props", json=prop_payload(game.id, line=300))

    assert res.status_code == 422
    assert (
        "Line must be a positive number ending in .5" in res.json()["detail"][0]["msg"]
    )
    assert test_db_session.query(Prop).count() == 0


def test_create_prop_for_missing_game_returns_404(admin_client):
    res = admin_client.post("/api/admin/props", json=prop_payload(999))

    assert res.status_code == 404
    assert res.json()["detail"] == "Game not found"


@pytest.mark.parametrize(
    ("kickoff_delta", "game_status"),
    [(timedelta(minutes=-1), "scheduled"), (timedelta(days=3), "postponed")],
)
def test_create_prop_for_closed_game_returns_400(
    admin_client, test_db_session, kickoff_delta, game_status
):
    game = add_game(test_db_session, kickoff_delta=kickoff_delta, status=game_status)

    res = admin_client.post("/api/admin/props", json=prop_payload(game.id))

    assert res.status_code == 400
    assert (
        res.json()["detail"] == "Game has already kicked off or is no longer scheduled"
    )


def test_create_duplicate_prop_returns_409(admin_client, test_db_session):
    game = add_game(test_db_session)
    add_prop(test_db_session, game)

    res = admin_client.post("/api/admin/props", json=prop_payload(game.id, line=280.5))

    assert res.status_code == 409
    assert test_db_session.query(Prop).count() == 1


def test_admin_can_publish_draft_prop(admin_client, test_db_session):
    prop = add_prop(test_db_session, add_game(test_db_session))

    res = admin_client.post(f"/api/admin/props/{prop.id}/publish")

    assert res.status_code == 200
    assert res.json()["status"] == "published"
    test_db_session.refresh(prop)
    assert prop.status == "published"


def test_publish_missing_prop_returns_404(admin_client):
    res = admin_client.post("/api/admin/props/999/publish")

    assert res.status_code == 404
    assert res.json()["detail"] == "Prop not found"


def test_publish_already_published_prop_returns_409(admin_client, test_db_session):
    prop = add_prop(test_db_session, add_game(test_db_session), status="published")

    res = admin_client.post(f"/api/admin/props/{prop.id}/publish")

    assert res.status_code == 409
    assert res.json()["detail"] == "Only draft props can be published"


def test_publish_after_kickoff_returns_400(admin_client, test_db_session):
    game = add_game(test_db_session, kickoff_delta=timedelta(minutes=-1))
    prop = add_prop(test_db_session, game)

    res = admin_client.post(f"/api/admin/props/{prop.id}/publish")

    assert res.status_code == 400
    test_db_session.refresh(prop)
    assert prop.status == "draft"


@pytest.mark.parametrize("path", ["/api/admin/props", "/api/admin/props/1/publish"])
def test_prop_routes_require_login(client, path):
    res = client.post(path, json=prop_payload(1))

    assert res.status_code == 401


@pytest.mark.parametrize("path", ["/api/admin/props", "/api/admin/props/1/publish"])
def test_prop_routes_reject_members(client, test_db_session, path):
    game = add_game(test_db_session)
    add_prop(test_db_session, game, player_name="Patrick Mahomes")
    login_as(client, test_db_session, "member")

    res = client.post(path, json=prop_payload(game.id))

    assert res.status_code == 403
    assert res.json()["detail"] == "Admin access required."
    assert test_db_session.query(Prop).one().status == "draft"


def test_admin_can_delete_draft_prop(admin_client, test_db_session):
    prop = add_prop(test_db_session, add_game(test_db_session))

    res = admin_client.delete(f"/api/admin/props/{prop.id}")

    assert res.status_code == 204
    assert res.content == b""
    assert test_db_session.query(Prop).count() == 0


@pytest.mark.parametrize("prop_status", ["published", "locked", "settled", "cancelled"])
def test_delete_non_draft_prop_returns_409(admin_client, test_db_session, prop_status):
    prop = add_prop(test_db_session, add_game(test_db_session), status=prop_status)

    res = admin_client.delete(f"/api/admin/props/{prop.id}")

    assert res.status_code == 409
    assert res.json()["detail"] == "Only draft props can be deleted"
    assert test_db_session.query(Prop).count() == 1


def test_delete_missing_prop_returns_404(admin_client):
    res = admin_client.delete("/api/admin/props/999")

    assert res.status_code == 404
    assert res.json()["detail"] == "Prop not found"


def test_delete_prop_requires_login(client):
    res = client.delete("/api/admin/props/1")

    assert res.status_code == 401


def test_delete_prop_rejects_members(client, test_db_session):
    add_prop(test_db_session, add_game(test_db_session))
    login_as(client, test_db_session, "member")

    res = client.delete("/api/admin/props/1")

    assert res.status_code == 403
    assert test_db_session.query(Prop).count() == 1
