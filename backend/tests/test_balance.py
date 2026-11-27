import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
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


def _create_user(
    db: Session,
    username: str = "player1",
    email: str = "player1@example.com",
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


def test_get_balance_requires_auth(client):
    res = client.get("/api/balance")
    assert res.status_code == 401


def test_restore_balance_requires_auth(client):
    res = client.post("/api/balance/restore")
    assert res.status_code == 401


def test_get_balance_with_positive_funds(client, test_db_session):
    _, headers = _create_user(test_db_session, balance=5000)
    res = client.get("/api/balance", headers=headers)
    assert res.status_code == 200
    assert res.json() == {
        "balance": 5000,
        "can_restore": False,
        "restore_amount": 1000,
    }


def test_restore_balance_fails_when_balance_positive(client, test_db_session):
    user, headers = _create_user(test_db_session, balance=1)
    res = client.post("/api/balance/restore", headers=headers)

    assert res.status_code == 400
    assert res.json()["detail"] == "Balance must be 0 before requesting restoration."

    test_db_session.refresh(user)
    assert user.balance == 1


def test_suspended_user_cannot_restore_balance(client, test_db_session):
    _, headers = _create_user(
        test_db_session, balance=0, account_status="suspended"
    )
    res = client.post("/api/balance/restore", headers=headers)
    assert res.status_code == 403

