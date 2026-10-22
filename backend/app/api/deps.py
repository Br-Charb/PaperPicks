from collections.abc import Generator
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import AUTH_COOKIE_NAME
from app.core.security import decode_access_token
from app.db import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Yields a database session and ensures it closes when the request ends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user( request: Request, 
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db), ) -> User:
    
    """Validates the JWT token from header or cookie and gets current authenticated user."""
    if hasattr(request.state, "user") and request.state.user is not None:
        return request.state.user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    raw_token = token or request.cookies.get(AUTH_COOKIE_NAME)
    if not raw_token:
        raise credentials_exception

    if raw_token.startswith("Bearer "):
        raw_token = raw_token[7:]

    payload = decode_access_token(raw_token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if user.account_status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended",
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Requires the authenticated user to have admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
