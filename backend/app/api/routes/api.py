from fastapi import APIRouter

from app.api.routes import admin, auth

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
