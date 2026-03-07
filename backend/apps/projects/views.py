"""
DRF views for the projects module.

All views are read-only and publicly accessible. Query optimisation
uses ``prefetch_related`` to prevent N+1 queries on the languages
many-to-many relationship.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from .models import Project
from .serializers import ProjectListSerializer


class ProjectListView(ListAPIView):
    """List all visible projects for the Forge gallery.

    Returns a paginated list of projects ordered by star count
    (descending). Supports filtering by ``status`` and searching
    by ``name``.

    Query Parameters:
        status: Filter by project status (Active, Beta, Alpha).
        search: Full-text search on project name/description.
        ordering: Override default ordering (e.g. ``?ordering=forks``).
        page: Page number.
        page_size: Items per page (max 100).
    """

    serializer_class = ProjectListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]
    ordering_fields = ["stars", "forks", "name", "created_at"]
    ordering = ["-stars"]

    def get_queryset(self):
        """Return visible projects with prefetched languages.

        Returns:
            QuerySet of visible Project instances with languages
            prefetched to avoid N+1 queries.
        """
        return (
            Project.objects.filter(is_visible=True)
            .prefetch_related("languages")
        )
