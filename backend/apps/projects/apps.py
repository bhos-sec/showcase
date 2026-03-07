"""Django app configuration for the projects module (The Forge)."""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Configuration for the projects application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "Projects (The Forge)"
