from fastapi import APIRouter

from app.api.routes import admin, admin_props, auth, balance, props

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(admin_props.router, prefix="/admin/props", tags=["admin"])
router.include_router(props.router, prefix="/props", tags=["props"])
router.include_router(balance.router, prefix="/balance", tags=["balance"])
