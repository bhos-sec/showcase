"""
Local development settings for the Showcase project.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# DRF — enable browsable API in development
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# ---------------------------------------------------------------------------
# Database — SQLite in project root
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ---------------------------------------------------------------------------
# Email — console backend for development
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Logging — add file handlers for local development
# ---------------------------------------------------------------------------
LOGGING["handlers"]["file"] = {  # noqa: F405
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": str(BASE_DIR / "logs" / "showcase.log"),  # noqa: F405
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "backupCount": 5,
    "formatter": "verbose",
}
LOGGING["handlers"]["celery_file"] = {  # noqa: F405
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": str(BASE_DIR / "logs" / "celery.log"),  # noqa: F405
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "backupCount": 5,
    "formatter": "celery",
}

# Update loggers to use file handlers
LOGGING["loggers"][""]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["celery"]["handlers"] = ["celery_console", "celery_file"]  # noqa: F405
LOGGING["loggers"]["celery.task"]["handlers"] = ["celery_console", "celery_file"]  # noqa: F405
LOGGING["loggers"]["celery.worker"]["handlers"] = ["celery_console", "celery_file"]  # noqa: F405
LOGGING["loggers"]["apps.projects"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["apps.members"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["apps.core"]["handlers"] = ["console", "file"]  # noqa: F405
