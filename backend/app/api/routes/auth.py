from fastapi import APIRouter, Response, status
from app.core.config import AUTH_COOKIE_NAME

router = APIRouter()


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    """Clears the HTTP-only authentication cookie to log the user out."""
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Successfully logged out"}
