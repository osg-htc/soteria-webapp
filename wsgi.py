#!/usr/bin/env python3

"""
WSGI application for the `registry` Flask application.

Log files will be placed in the Flask application's instance directory.
"""

import logging.config
import pathlib

import registry

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
LOG_DIR = THIS_DIR / "instance" / "log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] %(module)s:%(lineno)s ~ %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "default",
                "filename": LOG_DIR / "wsgi.log",
                "backupCount": 5,
                "maxBytes": 10 * 1024 * 1024,
            },
        },
        "root": {"level": "DEBUG", "handlers": ["file"]},
    }
)

application = registry.create_app()
