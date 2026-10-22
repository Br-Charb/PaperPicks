from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, field_validator

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserBase(BaseModel):
    username: str
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(EMAIL_REGEX, clean):
            raise ValueError("Invalid email format")
        return clean

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 3 or len(clean) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", clean):
            raise ValueError(
                "Username can only contain alphanumeric characters, underscores, dots, and dashes"
            )
        return clean


class UserRegister(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLogin(BaseModel):
    username_or_email: str | None = None
    email: str | None = None
    username: str | None = None
    password: str

    @property
    def identifier(self) -> str:
        ident = self.username_or_email or self.email or self.username
        if not ident:
            raise ValueError("Must provide email or username")
        return ident.strip()


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    balance: int
    account_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

CreateUser = UserRegister
LoginUser = UserLogin
Token = TokenResponse
