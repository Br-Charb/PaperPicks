import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.api.deps import get_current_user, get_db, require_admin
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


def test_logout_endpoint_clears_cookie(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None
    assert AUTH_COOKIE_NAME in set_cookie_header
    assert "max-age=0" in set_cookie_header.lower() or 'expires=' in set_cookie_header.lower()


def test_get_current_user_from_cookie(test_db_session):
    user = User(
        username="ryan",
        email="ryan@example.com",
        hashed_password="password",
        role="member",
        account_status="active",
    )
    test_db_session.add(user)
    test_db_session.commit()

    token = create_access_token({"sub": "ryan"})

    app = FastAPI()

    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    @app.get("/me")
    def me(current_user: User = Depends(get_current_user)):
        return {"username": current_user.username}

    with TestClient(app) as test_client:
        test_client.cookies.set(AUTH_COOKIE_NAME, token)
        res = test_client.get("/me")
        assert res.status_code == 200
        assert res.json() == {"username": "ryan"}

        test_client.cookies.clear()
        res_header = test_client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert res_header.status_code == 200
        assert res_header.json() == {"username": "ryan"}

        res_unauth = test_client.get("/me")
        assert res_unauth.status_code == 401


def test_get_current_user_suspended_blocks_access(test_db_session):
    suspended_user = User(
        username="banned_user",
        email="banned@example.com",
        hashed_password="password",
        role="member",
        account_status="suspended",
    )
    test_db_session.add(suspended_user)
    test_db_session.commit()

    token = create_access_token({"sub": "banned_user"})

    app = FastAPI()

    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    @app.get("/me")
    def me(current_user: User = Depends(get_current_user)):
        return {"username": current_user.username}

    with TestClient(app) as test_client:
        test_client.cookies.set(AUTH_COOKIE_NAME, token)
        res = test_client.get("/me")
        assert res.status_code == 403
        assert res.json()["detail"] == "Your account has been suspended"