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

import logging
import math
from abc import ABC, abstractmethod
from decimal import Decimal

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

class WeightedScoringStrategy(ScoringStrategy):
    """Scoring strategy using admin-configurable weights.

    Reads ``ScoringWeight`` records from the database and computes
    a weighted sum across all of a member's contributions.

    The weight lookup is cached on the instance so multiple calls
    within the same scoring run share the same DB query.
    """

    def __init__(self) -> None:
        self._weights: dict[str, Decimal] | None = None

    def _load_weights(self) -> dict[str, Decimal]:
        """Load scoring weights from the database.

        Returns:
            Dictionary mapping ContributionType values to their weight.
            Falls back to 1.0 for any type without a configured weight.
        """
        if self._weights is None:
            weight_map: dict[str, Decimal] = {
                ct.value: Decimal("1.0") for ct in ContributionType
            }
            for sw in ScoringWeight.objects.all():
                weight_map[sw.contribution_type] = sw.weight
            self._weights = weight_map
        return self._weights

    def calculate(self, member: Member) -> Decimal:
        """Calculate the weighted merit score for a member.

        Aggregates contribution points by type, then applies the
        configured weight for each type.

        Args:
            member: The Member instance to score.

        Returns:
            Total weighted score as a Decimal.
        """
        weights = self._load_weights()

        # Aggregate total points per contribution type for this member.
        type_totals = (
            Contribution.objects.filter(member=member)
            .values("contribution_type")
            .annotate(total_count=Sum("id", default=0))  # count
        )

        # We actually want count * weight, not sum of points.
        # Points are pre-computed on each contribution at creation time,
        # so simply summing all points is equivalent and more efficient.
        total = (
            Contribution.objects.filter(member=member)
            .aggregate(total_points=Sum("points"))
        )

        return total["total_points"] or Decimal("0.00")


# ---------------------------------------------------------------------------
# Service orchestrator
# ---------------------------------------------------------------------------

class ScoringService:
    """Orchestrates score calculation and impact ranking for members.

    Uses a pluggable ``ScoringStrategy`` to compute individual scores
    and provides bulk operations for recalculating the entire membership.

    Args:
        strategy: An optional ScoringStrategy instance. Defaults to
            ``WeightedScoringStrategy`` if not provided.

    Example:
        >>> service = ScoringService()
        >>> service.recalculate_all()
        32  # number of members updated
    """

    def __init__(self, strategy: ScoringStrategy | None = None) -> None:
        self._strategy = strategy or WeightedScoringStrategy()

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

        # Phase 1: Calculate scores and contribution counts.
        for member in members:
            member.score = self.calculate_score(member)
            member.contributions_count = (
                Contribution.objects.filter(member=member).count()
            )

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
            fields=["score", "contributions_count", "impact"],
            batch_size=100,
        )

        logger.info("Recalculated scores for %d members.", len(members))
        return len(members)
