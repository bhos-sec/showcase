"""
DRF views for the members module.

Provides read-only endpoints for the leaderboard and individual
member profiles. Query optimisation prevents N+1 queries through
strategic use of ``prefetch_related`` and ``select_related``.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Member
from .serializers import MemberDetailSerializer, MemberListSerializer


class MemberLeaderboardView(ListAPIView):
    """List all active members ranked by score (the Leaderboard).

    Returns a paginated, filterable list of members ordered by
    descending score. Supports filtering by ``tier`` and searching
    by ``name`` or ``github_username``.

    Query Parameters:
        tier: Filter by leadership tier (Founder, Lead, Mentor, etc.).
        search: Search by name or GitHub username.
        ordering: Override ordering (e.g. ``?ordering=-contributions_count``).
        page: Page number (25 per page by default).
        page_size: Items per page (max 100).
    """

    serializer_class = MemberListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tier"]
    search_fields = ["name", "github_username"]
    ordering_fields = ["score", "contributions_count", "impact", "name"]
    ordering = ["-score"]

    def get_queryset(self):
        """Return active members with prefetched badge relations.

        Returns:
            QuerySet of active Member instances with member_badges
            and badge prefetched to avoid N+1 queries.
        """
        return Member.objects.filter(is_active=True).prefetch_related(
            "member_badges__badge"
        )


class MemberDetailView(RetrieveAPIView):
    """Retrieve a single member's full profile with contributions.

    Includes recent contributions and a breakdown by contribution
    type, in addition to the standard leaderboard fields.
    """

    serializer_class = MemberDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        """Return active members with all related data prefetched.

        Returns:
            QuerySet with badges and contributions prefetched.
        """
        return Member.objects.filter(is_active=True).prefetch_related(
            "member_badges__badge",
            "contributions__repository",
        )
