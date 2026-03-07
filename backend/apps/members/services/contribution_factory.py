"""
Contribution factory for creating contribution records.

Implements the Factory pattern to normalise raw GitHub API data
into Contribution model instances. Each factory method handles a
specific contribution type, applying the correct scoring weight
and ensuring idempotent imports via ``github_id`` deduplication.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal

from django.utils.dateparse import parse_datetime

from apps.members.models import Contribution, ContributionType, Member, ScoringWeight
from apps.projects.models import Project

logger = logging.getLogger(__name__)


class ContributionFactory:
    """Factory for creating Contribution records from GitHub API data.

    All factory methods are idempotent — calling them with the same
    ``github_id`` will return the existing record without creating
    a duplicate.

    Class Methods:
        create_from_pull_request: Create from a merged PR.
        create_from_review: Create from a code review.
        create_from_issue: Create from a closed issue.
        create_from_commit: Create from a commit.

    Example:
        >>> contribution, created = ContributionFactory.create_from_pull_request(
        ...     member=member,
        ...     pr_data={"id": 123, "title": "Fix bug", ...},
        ... )
    """

    @classmethod
    def _get_weight(cls, contribution_type: str) -> Decimal:
        """Look up the scoring weight for a contribution type.

        Args:
            contribution_type: One of the ContributionType values.

        Returns:
            The configured weight, or 1.0 if not found.
        """
        try:
            sw = ScoringWeight.objects.get(contribution_type=contribution_type)
            return sw.weight
        except ScoringWeight.DoesNotExist:
            return Decimal("1.0")

    @classmethod
    def _resolve_repository(cls, repo_name: str | None) -> Project | None:
        """Resolve a repository name to a Project instance.

        Args:
            repo_name: The repository name (not full name).

        Returns:
            The matching Project or None if not found.
        """
        if not repo_name:
            return None
        return Project.objects.filter(name=repo_name).first()

    @classmethod
    def _parse_datetime(cls, dt_string: str | None) -> datetime | None:
        """Parse an ISO 8601 datetime string.

        Args:
            dt_string: ISO 8601 datetime string from GitHub.

        Returns:
            Parsed datetime or None.
        """
        if not dt_string:
            return None
        return parse_datetime(dt_string)

    @classmethod
    def create_from_pull_request(
        cls,
        member: Member,
        pr_data: dict,
        repository: Project | None = None,
    ) -> tuple[Contribution, bool]:
        """Create a contribution record from a merged pull request.

        Args:
            member: The member who authored the PR.
            pr_data: Raw PR data from the GitHub API. Expected keys:
                ``id``, ``title``, ``html_url``, ``merged_at``,
                ``additions``, ``deletions``, ``base.repo.name`` (optional).
            repository: Optional explicit Project link.

        Returns:
            Tuple of (Contribution, created) where created is True
            if a new record was made, False if it already existed.
        """
        github_id = f"pr_{pr_data['id']}"
        weight = cls._get_weight(ContributionType.PR_MERGED)

        if not repository:
            repo_name = pr_data.get("base", {}).get("repo", {}).get("name")
            repository = cls._resolve_repository(repo_name)

        occurred_at = cls._parse_datetime(
            pr_data.get("merged_at") or pr_data.get("closed_at") or pr_data.get("created_at")
        )

        additions = pr_data.get("additions", 0)
        deletions = pr_data.get("deletions", 0)

        contribution, created = Contribution.objects.get_or_create(
            github_id=github_id,
            defaults={
                "member": member,
                "contribution_type": ContributionType.PR_MERGED,
                "title": pr_data.get("title", "Untitled PR"),
                "url": pr_data.get("html_url", ""),
                "repository": repository,
                "points": weight,
                "additions": additions,
                "deletions": deletions,
                "occurred_at": occurred_at,
            },
        )
        
        # Update line stats if they were just fetched (non-zero values)
        if not created and (additions > 0 or deletions > 0):
            if contribution.additions != additions or contribution.deletions != deletions:
                contribution.additions = additions
                contribution.deletions = deletions
                contribution.save(update_fields=["additions", "deletions"])
        
        return contribution, created

    @classmethod
    def create_from_review(
        cls,
        member: Member,
        review_data: dict,
        repository: Project | None = None,
    ) -> tuple[Contribution, bool]:
        """Create a contribution record from a code review.

        Args:
            member: The member who submitted the review.
            review_data: Raw review data from the GitHub API. Expected keys:
                ``id``, ``html_url``, ``submitted_at``, ``pull_request_url``.
            repository: Optional explicit Project link.

        Returns:
            Tuple of (Contribution, created).
        """
        github_id = f"review_{review_data['id']}"
        weight = cls._get_weight(ContributionType.CODE_REVIEW)

        occurred_at = cls._parse_datetime(
            review_data.get("submitted_at") or review_data.get("created_at")
        )

        additions = review_data.get("additions", 0)
        deletions = review_data.get("deletions", 0)

        contribution, created = Contribution.objects.get_or_create(
            github_id=github_id,
            defaults={
                "member": member,
                "contribution_type": ContributionType.CODE_REVIEW,
                "title": f"Review on {review_data.get('pull_request_url', 'PR').split('/')[-1]}",
                "url": review_data.get("html_url", ""),
                "repository": repository,
                "points": weight,
                "additions": additions,
                "deletions": deletions,
                "occurred_at": occurred_at,
            },
        )
        
        # Update line stats if they were just fetched
        if not created and (additions > 0 or deletions > 0):
            if contribution.additions != additions or contribution.deletions != deletions:
                contribution.additions = additions
                contribution.deletions = deletions
                contribution.save(update_fields=["additions", "deletions"])
        
        return contribution, created

    @classmethod
    def create_from_issue(
        cls,
        member: Member,
        issue_data: dict,
        repository: Project | None = None,
    ) -> tuple[Contribution, bool]:
        """Create a contribution record from a closed issue.

        Args:
            member: The member who resolved the issue.
            issue_data: Raw issue data from the GitHub API. Expected keys:
                ``id``, ``title``, ``html_url``, ``closed_at``,
                ``repository.name`` (optional).
            repository: Optional explicit Project link.

        Returns:
            Tuple of (Contribution, created).
        """
        github_id = f"issue_{issue_data['id']}"
        weight = cls._get_weight(ContributionType.ISSUE_CLOSED)

        if not repository:
            repo_name = issue_data.get("repository", {}).get("name")
            repository = cls._resolve_repository(repo_name)

        occurred_at = cls._parse_datetime(
            issue_data.get("closed_at") or issue_data.get("created_at")
        )

        additions = issue_data.get("additions", 0)
        deletions = issue_data.get("deletions", 0)

        contribution, created = Contribution.objects.get_or_create(
            github_id=github_id,
            defaults={
                "member": member,
                "contribution_type": ContributionType.ISSUE_CLOSED,
                "title": issue_data.get("title", "Untitled Issue"),
                "url": issue_data.get("html_url", ""),
                "repository": repository,
                "points": weight,
                "additions": additions,
                "deletions": deletions,
                "occurred_at": occurred_at,
            },
        )
        
        # Update line stats if they were just fetched
        if not created and (additions > 0 or deletions > 0):
            if contribution.additions != additions or contribution.deletions != deletions:
                contribution.additions = additions
                contribution.deletions = deletions
                contribution.save(update_fields=["additions", "deletions"])
        
        return contribution, created

    @classmethod
    def create_from_commit(
        cls,
        member: Member,
        commit_data: dict,
        repository: Project | None = None,
    ) -> tuple[Contribution, bool]:
        """Create a contribution record from a commit.

        Args:
            member: The member who authored the commit.
            commit_data: Raw commit data. Expected keys:
                ``sha``, ``commit.message``, ``html_url``,
                ``commit.author.date``, ``additions``, ``deletions``.
            repository: Optional explicit Project link.

        Returns:
            Tuple of (Contribution, created).
        """
        github_id = f"commit_{commit_data.get('sha', commit_data.get('id', ''))}"
        weight = cls._get_weight(ContributionType.COMMIT)

        commit_info = commit_data.get("commit", {})
        occurred_at = cls._parse_datetime(
            commit_info.get("author", {}).get("date")
            or commit_data.get("created_at")
        )

        message = commit_info.get("message", "Untitled commit")
        # Truncate commit message to first line.
        title = message.split("\n", 1)[0][:500]

        additions = commit_data.get("additions", 0)
        deletions = commit_data.get("deletions", 0)

        contribution, created = Contribution.objects.get_or_create(
            github_id=github_id,
            defaults={
                "member": member,
                "contribution_type": ContributionType.COMMIT,
                "title": title,
                "url": commit_data.get("html_url", ""),
                "repository": repository,
                "points": weight,
                "additions": additions,
                "deletions": deletions,
                "occurred_at": occurred_at,
            },
        )
        
        # Update line stats if they were just fetched
        if not created and (additions > 0 or deletions > 0):
            if contribution.additions != additions or contribution.deletions != deletions:
                contribution.additions = additions
                contribution.deletions = deletions
                contribution.save(update_fields=["additions", "deletions"])
        
        return contribution, created
