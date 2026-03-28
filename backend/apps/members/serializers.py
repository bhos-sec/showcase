"""
DRF serializers for the members module.

Defines the API representation of Member and Badge records,
matching the data shapes expected by the React leaderboard.
"""

from rest_framework import serializers

from .models import Badge, Contribution, Member, MemberBadge


class BadgeSerializer(serializers.ModelSerializer):
    """Serializes a badge for display on member profiles.

    Fields:
        name: Badge display name (e.g. "Architect").
        icon_name: Frontend icon identifier.
        description: Optional explanation of the badge.
    """

    class Meta:
        model = Badge
        fields = ["name", "icon_name", "description"]


class MemberBadgeSerializer(serializers.ModelSerializer):
    """Serializes the through-model, exposing the badge name as a string.

    The frontend expects ``badges`` as a flat list of strings.
    """

    name = serializers.CharField(source="badge.name", read_only=True)

    class Meta:
        model = MemberBadge
        fields = ["name"]


class MemberListSerializer(serializers.ModelSerializer):
    """Serializes a member for the leaderboard list view.

    Matches the frontend contract::

        {
            id, name, tier, score, github, contributions,
            impact, additions, deletions, badges: string[], avatar
        }

    The ``badges`` field is flattened to a list of name strings.
    ``github`` maps to ``github_username``.
    ``contributions`` maps to ``contributions_count``.
    ``avatar`` maps to ``avatar_url``.
    """

    github = serializers.CharField(source="github_username", read_only=True)
    contributions = serializers.IntegerField(
        source="contributions_count", read_only=True
    )
    avatar = serializers.URLField(source="avatar_url", read_only=True)
    badges = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id",
            "name",
            "tier",
            "score",
            "monthly_score",
            "weekly_score",
            "github",
            "contributions",
            "monthly_contribution_count",
            "weekly_contribution_count",
            "impact",
            "weekly_impact",
            "monthly_impact",
            "additions",
            "weekly_additions",
            "monthly_additions",
            "deletions",
            "weekly_deletions",
            "monthly_deletions",
            "badges",
            "avatar",
        ]

    def get_badges(self, obj: Member) -> list[str]:
        """Return badges as a flat list of name strings.

        Args:
            obj: The Member instance being serialized.

        Returns:
            List of badge name strings.
        """
        return [mb.badge.name for mb in obj.member_badges.all()]


class ContributionSerializer(serializers.ModelSerializer):
    """Serializes a single contribution record.

    Used in the member detail view to show contribution history.
    """

    type_display = serializers.CharField(
        source="get_contribution_type_display", read_only=True
    )
    repository_name = serializers.CharField(
        source="repository.name", read_only=True, default=None
    )

    class Meta:
        model = Contribution
        fields = [
            "id",
            "contribution_type",
            "type_display",
            "title",
            "url",
            "repository_name",
            "points",
            "additions",
            "deletions",
            "occurred_at",
        ]


class MemberDetailSerializer(MemberListSerializer):
    """Extended member serializer with full contribution breakdown.

    Includes recent contributions and a breakdown of contribution
    counts by type.
    """

    recent_contributions = serializers.SerializerMethodField()
    contribution_breakdown = serializers.SerializerMethodField()

    class Meta(MemberListSerializer.Meta):
        fields = MemberListSerializer.Meta.fields + [
            "recent_contributions",
            "contribution_breakdown",
        ]

    def get_recent_contributions(self, obj: Member) -> list[dict]:
        """Return the 20 most recent contributions for the member.

        Args:
            obj: The Member instance being serialized.

        Returns:
            List of serialized contribution records.
        """
        recent = obj.contributions.select_related("repository")[:20]
        return ContributionSerializer(recent, many=True).data

    def get_contribution_breakdown(self, obj: Member) -> dict[str, int]:
        """Return contribution counts grouped by type.

        Args:
            obj: The Member instance being serialized.

        Returns:
            Dictionary mapping contribution type to count.
        """
        from django.db.models import Count

        qs = (
            obj.contributions.values("contribution_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return {entry["contribution_type"]: entry["count"] for entry in qs}
