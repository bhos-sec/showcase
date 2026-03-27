"""
Merit scoring service with Strategy pattern.

Implements the Meritocracy Engine's score calculation logic as a
pluggable strategy, allowing different scoring algorithms to be
swapped without modifying calling code.

Architecture:
    ScoringStrategy (ABC)
        └── WeightedScoringStrategy — reads admin-configurable weights
                                      from the database.

    ScoringService — orchestrator that delegates to a strategy and
                     manages bulk recalculation of all members.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from datetime import time
import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from time import time, timezone

from django.db.models import Sum

from apps.members.models import Contribution, ContributionType, Member, ScoringWeight

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Strategy interface
# ---------------------------------------------------------------------------


class ScoringStrategy(ABC):
    """Abstract base class for scoring algorithms.

    Subclass this to implement a new scoring strategy. The scoring
    service will call ``calculate()`` for each member.
    """

    @abstractmethod
    def calculate(self, member: Member) -> Decimal:
        """Calculate the merit score for a single member.

        Args:
            member: The Member instance to score.

        Returns:
            The computed score as a Decimal.
        """
        ...


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------


class ComprehensiveScoringStrategy(ScoringStrategy):
    """Comprehensive scoring strategy based on multiple contribution metrics.

    Calculates score based on:
    - Contributions count (highest priority): 5 points per contribution
    - Lines added (medium priority): 0.01 points per line
    - Lines deleted (medium priority): 0.005 points per line
    - Issues opened/closed (lower priority): 3 points per issue

    Formula:
        Score = (contributions × 5) + (additions × 0.01) +
                 (deletions × 0.005) + (issues × 3)
    """

    # Scoring weights - adjust these to change priority
    CONTRIBUTION_WEIGHT = Decimal("5")  # 5 points per contribution
    ADDITIONS_WEIGHT = Decimal("0.01")  # 0.01 points per line added
    DELETIONS_WEIGHT = Decimal("0.005")  # 0.005 points per line deleted
    ISSUE_WEIGHT = Decimal("3")  # 3 points per issue

    def calculate(self, member: Member) -> Decimal:
        """Calculate comprehensive merit score for a member.

        Aggregates scores from multiple metrics with weighted priorities.

        Args:
            member: The Member instance to score.

        Returns:
            Total weighted score as a Decimal.
        """
        score = Decimal("0")

        # 1. Contribution count score (highest priority)
        #
        # Non-commit types (PRs, reviews, issues): each record = 1 contribution.
        # Commit type: uses aggregated repo-stat records where
        #   points = commit_weight × total_commits_in_repo
        # Summing points and dividing by commit_weight recovers the effective
        # commit count, which is then multiplied by CONTRIBUTION_WEIGHT.
        non_commit_count = (
            Contribution.objects.filter(member=member)
            .exclude(contribution_type=ContributionType.COMMIT)
            .count()
        )
        commit_points = (
            Contribution.objects.filter(
                member=member, contribution_type=ContributionType.COMMIT
            ).aggregate(total=Sum("points", default=0))["total"]
            or 0
        )
        try:
            commit_weight = ScoringWeight.objects.get(
                contribution_type=ContributionType.COMMIT
            ).weight
        except ScoringWeight.DoesNotExist:
            commit_weight = Decimal("1.0")

        effective_commit_count = (
            Decimal(str(commit_points)) / commit_weight
            if commit_weight
            else Decimal("0")
        )
        contribution_count = non_commit_count + int(effective_commit_count)
        contribution_score = Decimal(contribution_count) * self.CONTRIBUTION_WEIGHT
        logger.debug(
            "Member %s: %d contributions × %s = %s",
            member.github_username,
            contribution_count,
            self.CONTRIBUTION_WEIGHT,
            contribution_score,
        )

        # 2. Lines added score
        line_stats = Contribution.objects.filter(member=member).aggregate(
            total_additions=Sum("additions", default=0),
            total_deletions=Sum("deletions", default=0),
        )

        additions = line_stats["total_additions"] or 0
        deletions = line_stats["total_deletions"] or 0

        additions_score = Decimal(additions) * self.ADDITIONS_WEIGHT
        deletions_score = Decimal(deletions) * self.DELETIONS_WEIGHT

        logger.debug(
            "Member %s: +%d lines × %s + -%d lines × %s = +%s -%s",
            member.github_username,
            additions,
            self.ADDITIONS_WEIGHT,
            deletions,
            self.DELETIONS_WEIGHT,
            additions_score,
            deletions_score,
        )

        # 3. Issues opened/closed score
        issue_count = Contribution.objects.filter(
            member=member, contribution_type=ContributionType.ISSUE_CLOSED
        ).count()
        issue_score = Decimal(issue_count) * self.ISSUE_WEIGHT

        logger.debug(
            "Member %s: %d issues × %s = %s",
            member.github_username,
            issue_count,
            self.ISSUE_WEIGHT,
            issue_score,
        )

        # Total score
        score = contribution_score + additions_score + deletions_score + issue_score

        logger.debug(
            "Member %s: Total score = %s + %s + %s + %s = %s",
            member.github_username,
            contribution_score,
            additions_score,
            deletions_score,
            issue_score,
            score,
        )

        return score


# ---------------------------------------------------------------------------
# Service orchestrator
# ---------------------------------------------------------------------------


class ScoringService:
    """Orchestrates score calculation and impact ranking for members.

    Uses a pluggable ``ScoringStrategy`` to compute individual scores
    and provides bulk operations for recalculating the entire membership.

    Uses ComprehensiveScoringStrategy by default, which scores based on:
    - Contribution count (5 points each)
    - Lines added (0.01 points each)
    - Lines deleted (0.005 points each)
    - Issues closed (3 points each)

    Args:
        strategy: An optional ScoringStrategy instance. Defaults to
            ``ComprehensiveScoringStrategy`` if not provided.

    Example:
        >>> service = ScoringService()
        >>> service.recalculate_all()
        32  # number of members updated
    """

    def __init__(self, strategy: ScoringStrategy | None = None) -> None:
        self._strategy = strategy or ComprehensiveScoringStrategy()

    @staticmethod
    def _as_start_of_day(day):
        tz = timezone.get_current_timezone()
        return timezone.make_aware(datetime.combine(day, time.min), tz)
    def _last_week_range(self):
        today = timezone.localdate()
        this_week_start = today - timedelta(days=today.weekday())   # Monday
        last_week_start = this_week_start - timedelta(days=7)
        return (
            self._as_start_of_day(last_week_start),  # inclusive
            self._as_start_of_day(this_week_start),  # exclusive
        )

    def _last_month_range(self):
        today = timezone.localdate()
        this_month_start = today.replace(day=1)
        last_month_end = this_month_start
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        return (
            self._as_start_of_day(last_month_start),  # inclusive
            self._as_start_of_day(last_month_end),    # exclusive
        )

    def calculate_score(self, member: Member) -> Decimal:
        """Calculate the merit score for a single member.

        Args:
            member: The Member instance to score.

        Returns:
            The computed score as a Decimal.
        """
        return self._strategy.calculate(member)

    def calculate_impact(self, member: Member) -> int:
        """Calculate a member's impact as score distribution percentage.

        Impact represents what percentage of the team's total score
        this member contributes. A score of 66 means this member
        accounts for 66% of all active members' combined score.

        Args:
            member: The Member instance to rank.

        Returns:
            Integer percentage of total score (0–100).
        """
        all_members = Member.objects.filter(is_active=True)
        total_score = sum(m.score for m in all_members)

        if total_score == 0:
            return 0  # No scores yet.

        member_percentage = (member.score / total_score) * 100
        return min(int(member_percentage), 100)

    def recalculate_all(self) -> int:
        """Recalculate scores and impact for all active members.

        Performs a bulk update for efficiency. This method should be
        called after contribution sync tasks complete.

        Returns:
            Number of members updated.
        """
        members = list(Member.objects.filter(is_active=True))

        if not members:
            return 0

        # Phase 1: Calculate scores, contribution counts, and line changes.
        for member in members:
            member.score = self.calculate_score(member)

            # contributions_count: reflect the effective number of individual
            # contributions, not raw DB record count. Commits use aggregated
            # repo-stat records where points = weight × commit_count, so we
            # recover the commit count via Sum(points) / weight.
            non_commit_count = (
                Contribution.objects.filter(member=member)
                .exclude(contribution_type=ContributionType.COMMIT)
                .count()
            )
            commit_points = (
                Contribution.objects.filter(
                    member=member, contribution_type=ContributionType.COMMIT
                ).aggregate(total=Sum("points", default=0))["total"]
                or 0
            )
            try:
                commit_weight = ScoringWeight.objects.get(
                    contribution_type=ContributionType.COMMIT
                ).weight
            except ScoringWeight.DoesNotExist:
                commit_weight = Decimal("1.0")

            effective_commit_count = (
                int(Decimal(str(commit_points)) / commit_weight) if commit_weight else 0
            )
            member.contributions_count = non_commit_count + effective_commit_count

            # Aggregate line changes from all contributions
            line_stats = Contribution.objects.filter(member=member).aggregate(
                total_additions=Sum("additions"),
                total_deletions=Sum("deletions"),
            )

            member.additions = line_stats["total_additions"] or 0
            member.deletions = line_stats["total_deletions"] or 0

        # Phase 2: Calculate impact (needs up-to-date scores).
        # Calculate each member's percentage of total score distribution.
        total_score = sum(m.score for m in members)

        for member in members:
            if total_score == 0:
                member.impact = 0
            else:
                member_percentage = (member.score / total_score) * 100
                member.impact = min(int(member_percentage), 100)

        # Phase 3: Bulk update.
        Member.objects.bulk_update(
            members,
            fields=["score", "contributions_count", "impact", "additions", "deletions"],
            batch_size=100,
        )

        logger.info("Recalculated scores for %d members.", len(members))
        return len(members)
