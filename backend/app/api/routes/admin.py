from fastapi import APIRouter, Depends

from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/dashboard")
def get_admin_dashboard(current_admin: User = Depends(require_admin)):
    """Admin dashboard endpoint accessible only to administrators."""
    return {
        "message": "Admin dashboard access granted",
        "admin": current_admin.username,
    }
