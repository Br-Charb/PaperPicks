from typing import Callable

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import OperationalError
from app.db import Base, engine
from app.models import Game, Prop, User


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        try:
            _ = (User, Game, Prop)
            Base.metadata.create_all(bind=engine)
        except OperationalError:
            logger.exception("failed to initialize database")

    return start_app
