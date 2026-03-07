"""Django admin configuration for the members module."""

from django.contrib import admin

from .models import Badge, Contribution, Member, MemberBadge, ScoringWeight


class MemberBadgeInline(admin.TabularInline):
    """Inline admin for assigning badges to members."""

    model = MemberBadge
    extra = 1
    autocomplete_fields = ["badge"]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin interface for collective members.

    The ``tier`` field is editable directly from the list view,
    giving admins quick control over leadership assignments.
    Cached score fields are read-only — they are recomputed by
    the scoring service.
    """

    list_display = (
        "name",
        "github_username",
        "tier",
        "score",
        "contributions_count",
        "impact",
        "is_active",
    )
    list_filter = ("tier", "is_active")
    list_editable = ("tier",)
    search_fields = ("name", "github_username")
    readonly_fields = (
        "score",
        "contributions_count",
        "impact",
        "created_at",
        "updated_at",
    )
    inlines = [MemberBadgeInline]
    ordering = ("-score",)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for achievement badges."""

    list_display = ("name", "icon_name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ScoringWeight)
class ScoringWeightAdmin(admin.ModelAdmin):
    """Admin interface for scoring weights.

    Weights are editable directly from the list view so admins
    can quickly tune the merit scoring engine.
    """

    list_display = ("contribution_type", "weight", "description")
    list_editable = ("weight",)
    ordering = ("-weight",)


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """Admin interface for viewing contribution records.

    Contributions are read-only — they are created by the GitHub
    sync service and should not be manually edited.
    """

    list_display = (
        "member",
        "contribution_type",
        "title",
        "points",
        "occurred_at",
    )
    list_filter = ("contribution_type",)
    search_fields = ("title", "member__name", "member__github_username")
    readonly_fields = (
        "member",
        "contribution_type",
        "github_id",
        "title",
        "url",
        "repository",
        "points",
        "occurred_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-occurred_at",)

    def has_add_permission(self, request):
        """Disable manual creation of contribution records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable manual editing of contribution records."""
        return False
