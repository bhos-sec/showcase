"""Django app configuration for the members module."""

from django.apps import AppConfig


class MembersConfig(AppConfig):
    """Configuration for the members application (Meritocracy Engine)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.members"
    verbose_name = "Members (Meritocracy)"
