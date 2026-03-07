"""
Data models for the projects (Forge) module.

Represents the collective's open-source repositories with live
GitHub statistics. Data is periodically synchronised from the
GitHub REST API by the ``sync_github_repos`` Celery task.
"""

from django.db import models

from apps.core.models import TimeStampedModel


class Language(TimeStampedModel):
    """A programming language used in one or more projects.

    Attributes:
        name: The canonical name of the language (e.g. "Python").
        color: Optional hex colour code from GitHub (e.g. "#3572A5").
    """

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Hex colour code from GitHub, e.g. '#3572A5'.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Project(TimeStampedModel):
    """An open-source repository belonging to the collective.

    Attributes:
        name: Repository name.
        description: Short description from GitHub.
        github_url: Full URL to the repository.
        homepage_url: Optional project homepage / docs URL.
        stars: Current star count.
        forks: Current fork count.
        open_issues: Current open issue count.
        status: Human-curated project maturity status.
        languages: Programming languages used (many-to-many).
        github_id: GitHub's internal repository ID for deduplication.
        last_synced_at: Timestamp of the most recent successful sync.
        is_visible: Admin toggle to hide repositories from the public API.
    """

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        BETA = "Beta", "Beta"
        ALPHA = "Alpha", "Alpha"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    github_url = models.URLField(unique=True)
    homepage_url = models.URLField(blank=True, default="")

    # Live statistics — updated by the sync task.
    stars = models.PositiveIntegerField(default=0, db_index=True)
    forks = models.PositiveIntegerField(default=0)
    open_issues = models.PositiveIntegerField(default=0)

    # Admin-controlled metadata.
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    languages = models.ManyToManyField(Language, blank=True, related_name="projects")
    is_visible = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this repo from the public Forge.",
    )

    # GitHub sync metadata.
    github_id = models.PositiveBigIntegerField(unique=True, help_text="GitHub repo ID.")
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-stars", "name"]
        indexes = [
            models.Index(fields=["-stars"], name="idx_project_stars_desc"),
        ]

    def __str__(self) -> str:
        return self.name
