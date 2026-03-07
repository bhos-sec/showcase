"""Django app configuration for the core shared module."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application providing shared foundations."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
