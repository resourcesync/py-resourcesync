# -*- coding: utf-8 -*-


import logging
from logging import NullHandler
from logging.config import dictConfig

__title__ = "py-resourcesync"

"""
logging_config = dict(
    version = 1,
    formatters = {
        "f": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s: %(message)s"
        }
    },
    handlers = {
        "h": {
            "class": "logging.Handler",
            "formatter": "f",
            "level": logging.DEBUG
        }
    },
    root = {
        "handlers": ["h"],
        "level": logging.DEBUG
    }
)
dictConfig(logging_config)
logging.getLogger(__name__).addHandler(NullHandler())
"""
