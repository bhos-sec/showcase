"""Django admin configuration for the projects module."""

from django.contrib import admin

from .models import Language, Project


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin interface for programming languages."""

    list_display = ("name", "color", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects (The Forge).

    Synced fields (stars, forks, open_issues, github_id, last_synced_at)
    are read-only — they are managed by the Celery sync task.
    Admins control ``status`` and ``is_visible`` to curate the Forge.
    """

    list_display = (
        "name",
        "stars",
        "forks",
        "status",
        "is_visible",
        "last_synced_at",
    )
    list_filter = ("status", "is_visible")
    list_editable = ("status", "is_visible")
    search_fields = ("name", "description")
    readonly_fields = (
        "github_id",
        "stars",
        "forks",
        "open_issues",
        "last_synced_at",
        "created_at",
        "updated_at",
    )
    filter_horizontal = ("languages",)
    ordering = ("-stars",)
