import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base
from app.models import User


# Creates temp database for testing
@pytest.fixture
def database_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_user(**overrides) -> User:
    user_data = {
        "username": "ben",
        "email": "ben@example.com",
        "password_hash": "hashed-password",
    }
    user_data.update(overrides)
    return User(**user_data)


def test_user_schema_has_named_unique_constraints():
    constraint_names = {constraint.name for constraint in User.__table__.constraints}

    assert "uq_users_email" in constraint_names
    assert "uq_users_username" in constraint_names


@pytest.mark.parametrize(
    ("first_user", "duplicate_user"),
    [
        (
            make_user(),
            make_user(username="different", email="ben@example.com"),
        ),
        (
            make_user(),
            make_user(username="ben", email="different@example.com"),
        ),
    ],
)
def test_user_email_and_username_must_be_unique(
    database_engine, first_user, duplicate_user
):
    with Session(database_engine) as session:
        session.add(first_user)
        session.commit()

        session.add(duplicate_user)
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize("required_field", ["username", "email", "password_hash"])
def test_required_user_fields_cannot_be_null(database_engine, required_field):
    user = make_user(**{required_field: None})

    with Session(database_engine) as session:
        session.add(user)
        with pytest.raises(IntegrityError):
            session.commit()


def test_new_user_receives_default_balance(database_engine):
    user = make_user()

    with Session(database_engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.balance == 10_000
