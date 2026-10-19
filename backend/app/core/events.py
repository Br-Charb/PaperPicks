from typing import Callable

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.models import User


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        try:
            _ = User
            Base.metadata.create_all(bind=engine)
        except OperationalError:
            logger.exception("failed to initialize database")

    return start_app
