from contextlib import asynccontextmanager

from app.api.routes.api import router as api_router
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from app.core.events import create_start_app_handler
from app.core.middleware import AdminAuthMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def lifespan(application: FastAPI):
    create_start_app_handler(application)()
    yield


def get_application() -> FastAPI:
    application = FastAPI(
        title=PROJECT_NAME, debug=DEBUG, version=VERSION, lifespan=lifespan
    )
    application.add_middleware(AdminAuthMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=API_PREFIX)
    return application


app = get_application()
