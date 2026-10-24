from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.deps import get_db
from app.core.config import API_PREFIX, AUTH_COOKIE_NAME
from app.core.security import decode_access_token
from app.db import SessionLocal
from app.models.user import User


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    Authorization middleware that intercepts any requests to admin API routes
    and blocks unauthenticated, non-admin, or suspended users.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        admin_prefix = f"{API_PREFIX}/admin"

        if not request.url.path.startswith(admin_prefix) or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        token: str | None = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif auth_header:
            token = auth_header.strip()
        else:
            token = request.cookies.get(AUTH_COOKIE_NAME)

        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token.startswith("Bearer "):
            token = token[7:].strip()

        payload = decode_access_token(token)
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        db = None
        db_gen = None
        override = getattr(request.app, "dependency_overrides", {}).get(get_db)
        if override:
            res = override()
            if hasattr(res, "__next__"):
                db_gen = res
                db = next(db_gen)
            else:
                db = res
        else:
            session_factory = getattr(request.app.state, "session_factory", SessionLocal)
            db = session_factory()

        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Could not validate credentials"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if user.account_status == "suspended":
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Your account has been suspended"},
                )

            if user.role != "admin":
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Admin access required."},
                )

            request.state.user = user
        finally:
            if db_gen:
                try:
                    next(db_gen)
                except StopIteration:
                    pass
            elif db:
                db.close()

        return await call_next(request)
