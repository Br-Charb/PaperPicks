from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app.core import events
from app.main import get_application


def test_create_start_app_handler(monkeypatch):
    def fake_create_all(*args, **kwargs):
        raise OperationalError("stmt", {}, Exception("db down"))

    monkeypatch.setattr(events.Base.metadata, "create_all", fake_create_all)

    app = FastAPI()
    handler = events.create_start_app_handler(app)
    handler()


def test_get_application():
    app = get_application()
    assert isinstance(app, FastAPI)
