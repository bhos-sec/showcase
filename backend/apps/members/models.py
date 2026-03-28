"""
Data models for the members (Meritocracy Engine) module.

Defines the Member, Badge, Contribution, and ScoringWeight models
that power the leaderboard, tiered leadership system, and weighted
merit scoring engine.
"""

from django.db import models

from apps.core.models import TimeStampedModel

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Tier(models.TextChoices):
    """Leadership tiers for the collective's ranking system.

    Tiers are admin-managed — members do not self-assign.
    Ordered from highest to lowest authority.
    """

    FOUNDER = "Founder", "Founder"
    LEAD = "Lead", "Lead"
    MENTOR = "Mentor", "Mentor"
    MEMBER = "Member", "Member"
    LEARNER = "Learner", "Learner"


class ContributionType(models.TextChoices):
    """Types of trackable contributions from GitHub activity.

    Each type has an associated weight in the ScoringWeight model
    that determines its value in the merit scoring engine.
    """

    PR_MERGED = "PR_MERGED", "Pull Request Merged"
    CODE_REVIEW = "CODE_REVIEW", "Code Review"
    ISSUE_CLOSED = "ISSUE_CLOSED", "Issue Closed"
    COMMIT = "COMMIT", "Commit"
    RELEASE = "RELEASE", "Release"
    DISCUSSION = "DISCUSSION", "Discussion"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Badge(TimeStampedModel):
    """An achievement badge that can be awarded to members.

    Badges are defined by admins and awarded through the MemberBadge
    through-model. They appear on the leaderboard alongside member
    profiles.

    Attributes:
        name: Unique display name (e.g. "Architect", "Reviewer").
        description: Optional explanation of how the badge is earned.
        icon_name: Identifier for the frontend icon component.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    icon_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Icon identifier for the frontend (e.g. 'Architect').",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Member(TimeStampedModel):
    """A member of the collective with their aggregated metrics.

    Members are identified by their GitHub username and are synced
    from the GitHub API. Leadership tier is admin-controlled.
    The ``score``, ``contributions_count``, and ``impact`` fields
    are cached values recomputed by the scoring engine.

    Attributes:
        name: Display name (from GitHub profile or admin override).
        github_username: Unique GitHub handle for API lookups.
        avatar_url: URL to the member's GitHub avatar.
        tier: Admin-assigned leadership tier.
        score: Cached weighted merit score.
        monthly_score: Cached weighted merit score for the current month.
        weekly_score: Cached weighted merit score for the current week.
        weekly_contribution_count: Cached contributions in the last week.
        monthly_contribution_count: Cached contributions in the last month.
        contributions_count: Cached total contribution count.
        impact: Cached percentile rank (0–100) among active members.
        badges: Earned badges via MemberBadge through-model.
        is_active: Soft-delete flag; inactive members are hidden.
    """

    name = models.CharField(max_length=255)
    github_username = models.CharField(max_length=100, unique=True, db_index=True)
    avatar_url = models.URLField(blank=True, default="")

    # Leadership — admin-managed.
    tier = models.CharField(
        max_length=10,
        choices=Tier.choices,
        default=Tier.LEARNER,
        db_index=True,
    )

    # Cached metrics — recomputed by the scoring service.
    #Weekly/Monthly/Total Scores
    score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Weighted merit score (cached, recomputed periodically).",
    )
    monthly_score=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Monthly weighted merit score (cached, recomputed periodically).",
    )
    weekly_score=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Weekly weighted merit score (cached, recomputed periodically).",
    )
    #Weekly/Monthly/Total Contribution Counts
    weekly_contribution_count=models.PositiveIntegerField(
        default=0,
        help_text="Total contributions in last week (cached).",
    )
    monthly_contribution_count=models.PositiveIntegerField(
        default=0,
        help_text="Total contributions in last month (cached).",
    )
    contributions_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of tracked contributions (cached).",
    )
    impact = models.PositiveIntegerField(
        default=0,
        help_text="Percentile rank among active members, 0–100 (cached).",
    )
    additions = models.PositiveIntegerField(
        default=0,
        help_text="Total lines added across all contributions (cached).",
    )
    deletions = models.PositiveIntegerField(
        default=0,
        help_text="Total lines deleted across all contributions (cached).",
    )

    # Badges — many-to-many via through model for metadata.
    badges = models.ManyToManyField(
        Badge,
        through="MemberBadge",
        blank=True,
        related_name="members",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-score", "name"]
        indexes = [
            models.Index(fields=["-score"], name="idx_member_score_desc"),
        ]

    def __str__(self) -> str:
        return f"{self.name} (@{self.github_username})"


class MemberBadge(TimeStampedModel):
    """Through-model linking a Member to a Badge with optional context.

    Attributes:
        member: The member who earned the badge.
        badge: The badge that was awarded.
        reason: Optional explanation for why the badge was given.
    """

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="member_badges",
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="badge_members",
    )
    reason = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = ("member", "badge")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.member.name} — {self.badge.name}"


class ScoringWeight(TimeStampedModel):
    """Admin-configurable weight for a contribution type.

    The scoring engine reads these weights when calculating member
    scores. Changing a weight and triggering a recalculation will
    update all member scores retroactively.

    Attributes:
        contribution_type: The type of contribution this weight applies to.
        weight: Numeric multiplier (e.g. 10.0 for merged PRs).
        description: Admin-facing description of this weight.
    """

    contribution_type = models.CharField(
        max_length=20,
        choices=ContributionType.choices,
        unique=True,
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=1.0,
        help_text="Points awarded per contribution of this type.",
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-weight"]

    def __str__(self) -> str:
        return f"{self.get_contribution_type_display()}: {self.weight}pts"


class Contribution(TimeStampedModel):
    """A single tracked contribution from a member's GitHub activity.

    Contributions are created by the GitHub profile sync service and
    scored using the associated ScoringWeight. The ``github_id`` field
    ensures idempotent imports — re-syncing the same data will not
    create duplicates.

    Attributes:
        member: The member who made the contribution.
        contribution_type: Category of the contribution.
        github_id: Unique identifier from GitHub for deduplication.
        title: Human-readable title (e.g. PR title, issue title).
        url: Link back to the contribution on GitHub.
        repository: Optional link to the related Project.
        points: Computed point value based on the scoring weight.
        additions: Lines of code added in this contribution.
        deletions: Lines of code deleted in this contribution.
        weekly_commits: Commit count in the current calendar week.
        monthly_commits: Commit count in the current calendar month.
        weekly_points: Weighted points in the current calendar week.
        monthly_points: Weighted points in the current calendar month.
        weekly_additions: Lines added in the current calendar week.
        weekly_deletions: Lines deleted in the current calendar week.
        monthly_additions: Lines added in the current calendar month.
        monthly_deletions: Lines deleted in the current calendar month.
        occurred_at: When the contribution occurred on GitHub.
    """

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    contribution_type = models.CharField(
        max_length=20,
        choices=ContributionType.choices,
        db_index=True,
    )
    github_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique GitHub identifier for deduplication.",
    )
    title = models.CharField(max_length=500)
    url = models.URLField(blank=True, default="")
    repository = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contributions",
    )
    points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Computed point value based on scoring weight.",
    )
    additions = models.PositiveIntegerField(
        default=0,
        help_text="Lines of code added in this contribution.",
    )
    deletions = models.PositiveIntegerField(
        default=0,
        help_text="Lines of code deleted in this contribution.",
    )
    weekly_commits = models.PositiveIntegerField(
        default=0,
        help_text="Commit count in the current calendar week.",
    )
    monthly_commits = models.PositiveIntegerField(
        default=0,
        help_text="Commit count in the current calendar month.",
    )
    weekly_points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Weighted points in the current calendar week.",
    )
    monthly_points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Weighted points in the current calendar month.",
    )
    weekly_additions = models.PositiveIntegerField(
        default=0,
        help_text="Lines added in the current calendar week.",
    )
    weekly_deletions = models.PositiveIntegerField(
        default=0,
        help_text="Lines deleted in the current calendar week.",
    )
    monthly_additions = models.PositiveIntegerField(
        default=0,
        help_text="Lines added in the current calendar month.",
    )
    monthly_deletions = models.PositiveIntegerField(
        default=0,
        help_text="Lines deleted in the current calendar month.",
    )
    occurred_at = models.DateTimeField(
        help_text="When this contribution occurred on GitHub.",
    )

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(
                fields=["member", "contribution_type"],
                name="idx_contrib_member_type",
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.get_contribution_type_display()}] {self.title}"
