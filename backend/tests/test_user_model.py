import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base
from app.models import User

#Creates temp database for testing
@pytest.fixture
def database_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

#Function to create base user for testing
def make_user(**overrides) -> User:
    user_data = {
        "username": "ben",
        "email": "ben@example.com",
        "password_hash": "hashed-password",
        "balance": 0,
    }
    user_data.update(overrides)
    return User(**user_data)

#Check that email and username have unique constraint
def test_user_schema_has_named_unique_constraints():
    constraint_names = {constraint.name for constraint in User.__table__.constraints}

    assert "uq_users_email" in constraint_names
    assert "uq_users_username" in constraint_names

#Verifies that same username or same email cannot be used
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

#Verifies that a value must be input for username, email, password_hash, and balance to be a valid creation
@pytest.mark.parametrize(
    "required_field", ["username", "email", "password_hash", "balance"]
)
def test_required_user_fields_cannot_be_null(database_engine, required_field):
    user = make_user(**{required_field: None})

    with Session(database_engine) as session:
        session.add(user)
        with pytest.raises(IntegrityError):
            session.commit()
