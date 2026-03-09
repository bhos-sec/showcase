"""Views for rendering leaderboard as web pages (not just API)."""

from django.shortcuts import render
from rest_framework.generics import ListAPIView

from .models import Member
from .serializers import MemberListSerializer


class LeaderboardHTMLView(ListAPIView):
    """Render leaderboard as HTML page for README embeds and direct viewing.

    Accessible at: /leaderboard/md/

    Query Parameters:
        top: Number of top members to show (default: 10, max: 100)
        format: 'html' (default) or 'table' for just the table
    """

    serializer_class = MemberListSerializer

    def get_queryset(self):
        """Return active members with prefetched badge relations."""
        return Member.objects.filter(is_active=True).prefetch_related(
            "member_badges__badge"
        ).order_by("-score")

    def get(self, request, *args, **kwargs):
        """Override to return HTML instead of JSON."""
        top = int(request.query_params.get('top', 10))
        format_type = request.query_params.get('format', 'html')

        # Limit to max 100
        top = min(top, 100)

        queryset = self.get_queryset()[:top]
        serializer = self.get_serializer(queryset, many=True)
        members_data = serializer.data

        context = {
            'members': members_data,
            'top': top,
            'total_count': self.get_queryset().count(),
        }

        if format_type == 'table':
            return render(request, 'leaderboard_table.html', context)

        return render(request, 'leaderboard_html.html', context)
