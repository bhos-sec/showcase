"""
DRF views for the members module.

Provides read-only endpoints for the leaderboard and individual
member profiles. Query optimisation prevents N+1 queries through
strategic use of ``prefetch_related`` and ``select_related``.
"""

import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Member
from .serializers import MemberDetailSerializer, MemberListSerializer

logger = logging.getLogger(__name__)


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


class LeaderboardHTMLView(View):
    """Render leaderboard as a styled HTML page for GitHub README embeds.

    Accessible at: /members/public/

    Query Parameters:
        top: Number of top members to show (default: 10, max: 100)

    Example:
        https://example.com/members/public/?top=10
    """

    def get(self, request, *args, **kwargs):
        """Return HTML page with leaderboard table."""
        top = int(request.GET.get("top", 10))

        # Limit to max 100
        top = min(top, 100)

        # Fetch members
        queryset = (
            Member.objects.filter(is_active=True)
            .prefetch_related("member_badges__badge")
            .order_by("-score")[:top]
        )

        # Serialize
        serializer = MemberListSerializer(queryset, many=True)
        members_data = serializer.data

        context = {
            "members": members_data,
            "top": len(members_data),
            "total_count": Member.objects.filter(is_active=True).count(),
        }

        return render(request, "leaderboard_public.html", context)


class LeaderboardTableView(View):
    """Render only the leaderboard table for embedding.

    Accessible at: /members/leaderboard-table/

    Query Parameters:
        top: Number of top members to show (default: 10, max: 100)

    Example:
        https://example.com/members/leaderboard-table/?top=15
    """

    def get(self, request, *args, **kwargs):
        """Return HTML page with table only."""
        top = int(request.GET.get("top", 10))
        top = min(top, 100)

        queryset = (
            Member.objects.filter(is_active=True)
            .prefetch_related("member_badges__badge")
            .order_by("-score")[:top]
        )

        serializer = MemberListSerializer(queryset, many=True)

        context = {
            "members": serializer.data,
            "top": len(serializer.data),
            "total_count": Member.objects.filter(is_active=True).count(),
        }

        return render(request, "leaderboard_table.html", context)


class LeaderboardImageView(View):
    """Generate leaderboard table as PNG image for README embedding.

    Accessible at: /members/leaderboard-image/

    Query Parameters:
        top: Number of top members to show (default: 10, max: 100)

    Returns:
        PNG image of the leaderboard table

    Example:
        https://example.com/members/leaderboard-image/?top=15
    """

    def get(self, request, *args, **kwargs):
        """Return PNG image of leaderboard table."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error(
                "Playwright not installed. Install with: pip install playwright"
            )
            return HttpResponse("Playwright not installed", status=500)

        top = int(request.GET.get("top", 10))
        top = min(top, 100)

        # Fetch members
        queryset = (
            Member.objects.filter(is_active=True)
            .prefetch_related("member_badges__badge")
            .order_by("-score")[:top]
        )

        serializer = MemberListSerializer(queryset, many=True)

        context = {
            "members": serializer.data,
            "top": len(serializer.data),
            "total_count": Member.objects.filter(is_active=True).count(),
        }

        # Render HTML
        html_content = render(
            request, "leaderboard_table.html", context
        ).content.decode("utf-8")

        # Convert HTML to PNG
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                # Create page with specific viewport width
                page = browser.new_page(viewport={"width": 1200, "height": 2000})
                page.set_content(html_content)

                # Wait for page to be ready (with timeout)
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    logger.warning("Page load timeout, proceeding with screenshot")

                # Get table bounding box to calculate exact size needed
                table_element = page.query_selector("table")
                if table_element:
                    box = table_element.bounding_box()
                    if box:
                        # Add minimal padding (32px = 2rem from CSS)
                        padding = 32
                        screenshot = page.screenshot(
                            type="png",
                            clip={
                                "x": 0,
                                "y": max(0, box["y"] - padding),
                                "width": 1200,
                                "height": box["height"] + (padding * 2),
                            },
                        )
                    else:
                        screenshot = page.screenshot(type="png", full_page=True)
                else:
                    screenshot = page.screenshot(type="png", full_page=True)

                browser.close()

            # Return PNG with CORS headers
            response = HttpResponse(screenshot, content_type="image/png")
            response["Cache-Control"] = "public, max-age=3600"
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            return response

        except Exception as e:
            logger.error(f"Failed to generate leaderboard image: {str(e)}", exc_info=True)
            return HttpResponse(f"Failed to generate image: {str(e)}", status=500)
