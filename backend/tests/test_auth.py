import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.api.deps import get_current_user, get_db
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


def test_register_new_user(client, test_db_session):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "strongpassword123",
    }
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["role"] == "member"
    assert data["user"]["balance"] == 10000
    assert data["user"]["account_status"] == "active"
    assert "access_token" in data

    set_cookie_header = response.headers.get("set-cookie", "")
    assert AUTH_COOKIE_NAME in set_cookie_header

    db_user = test_db_session.query(User).filter(User.username == "newuser").first()
    assert db_user is not None


def test_register_duplicate_username_fails(client, test_db_session):
    payload1 = {
        "username": "duplicate_user",
        "email": "user1@example.com",
        "password": "password123",
    }
    res1 = client.post("/api/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "username": "duplicate_user",
        "email": "user2@example.com",
        "password": "password123",
    }
    res2 = client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Username already registered"


def test_register_duplicate_email_fails(client, test_db_session):
    payload1 = {
        "username": "user_one",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    res1 = client.post("/api/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "username": "user_two",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    res2 = client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered"


def test_login_success_with_username_and_email(client, test_db_session):
    client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "password123",
        },
    )
    client.cookies.clear()

    res_user = client.post(
        "/api/auth/login",
        json={"username": "loginuser", "password": "password123"},
    )
    assert res_user.status_code == 200
    assert res_user.json()["user"]["username"] == "loginuser"
    assert AUTH_COOKIE_NAME in res_user.headers.get("set-cookie", "")

    client.cookies.clear()
    res_email = client.post(
        "/api/auth/login",
        json={"email": "loginuser@example.com", "password": "password123"},
    )
    assert res_email.status_code == 200
    assert res_email.json()["user"]["username"] == "loginuser"


def test_login_invalid_credentials(client):
    res = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "wrongpassword"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid username/email or password"


def test_get_me_endpoint(client):
    reg_res = client.post(
        "/api/auth/register",
        json={
            "username": "ryan",
            "email": "ryan@example.com",
            "password": "password",
        },
    )
    assert reg_res.status_code == 201

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "ryan"
    assert me_res.json()["email"] == "ryan@example.com"

    client.cookies.clear()
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401


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