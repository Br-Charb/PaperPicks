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
from app.models.user import User


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


def test_admin_route_unauthenticated_returns_401(client):
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_admin_route_invalid_token_returns_401(client):
    client.cookies.set(AUTH_COOKIE_NAME, "invalid-token")
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_admin_route_nonexistent_user_returns_401(client):
    token = create_access_token({"sub": "nonexistent_user"})
    client.cookies.set(AUTH_COOKIE_NAME, token)
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_admin_route_member_returns_403(client, test_db_session):
    member = User(
        username="ben",
        email="ben@example.com",
        hashed_password="password",
        role="member",
        account_status="active",
    )
    test_db_session.add(member)
    test_db_session.commit()

    token = create_access_token({"sub": "ben"})

    client.cookies.set(AUTH_COOKIE_NAME, token)
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 403
    assert res.json()["detail"] == "Admin access required."

    client.cookies.clear()
    res_header = client.get(
        "/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"}
    )
    assert res_header.status_code == 403
    assert res_header.json()["detail"] == "Admin access required."


def test_admin_route_suspended_admin_returns_403(client, test_db_session):
    suspended_admin = User(
        username="suspended_admin",
        email="suspendedadmin@example.com",
        hashed_password="password",
        role="admin",
        account_status="suspended",
    )
    test_db_session.add(suspended_admin)
    test_db_session.commit()

    token = create_access_token({"sub": "suspended_admin"})
    client.cookies.set(AUTH_COOKIE_NAME, token)
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 403
    assert res.json()["detail"] == "Your account has been suspended"


def test_admin_middleware_bypasses_options_preflight(client):
    res = client.options("/api/admin/dashboard")
    assert res.status_code != 401
    assert res.status_code != 403


def test_non_admin_route_not_blocked_by_admin_middleware(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
