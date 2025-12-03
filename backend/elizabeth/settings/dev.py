import os

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SUPERUSER_EMAIL = os.environ.get("SUPERUSER_EMAIL", default="mail@example.com")
SUPERUSER_PASSWORD = os.environ.get(
    "SUPERUSER_PASSWORD", default="SuperSecretPassword123"
)
SUPERUSER_PHONE = os.environ.get("SUPERUSER_PHONE", default="+790012345678")
SUPERUSER_FIRST_NAME = os.environ.get("SUPERUSER_FIRST_NAME", default="Test")
SUPERUSER_LAST_NAME = os.environ.get("SUPERUSER_LAST_NAME", default="User")
SUPERUSER_COUNTRY = os.environ.get("SUPERUSER_COUNTRY", default="RU")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "httpx": {"handlers": ["console"], "level": "DEBUG"},
        "backend.apps.providers.armtek": {"handlers": ["console"], "level": "DEBUG"},
    },
}
