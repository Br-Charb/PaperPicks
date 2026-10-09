import logging

from app.core import config


def test_config_defaults():
    assert config.API_PREFIX == "/api"
    assert config.PROJECT_NAME == "PaperPicks"
    assert config.LOGGING_LEVEL in (logging.INFO, logging.DEBUG)
