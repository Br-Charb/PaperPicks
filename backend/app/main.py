from contextlib import asynccontextmanager

from app.api.routes.api import router as api_router
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from app.core.events import create_start_app_handler
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(application: FastAPI):
    create_start_app_handler(application)()
    yield


def get_application() -> FastAPI:
    application = FastAPI(
        title=PROJECT_NAME, debug=DEBUG, version=VERSION, lifespan=lifespan
    )
    application.include_router(api_router, prefix=API_PREFIX)
    return application


app = get_application()
