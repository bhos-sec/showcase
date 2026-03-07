"""
Root URL configuration for the Showcase project.

Routes:
    /admin/          — Django admin interface.
    /api/projects/   — Project (Forge) endpoints.
    /api/members/    — Member (Leaderboard) endpoints.
    /api/health/     — Simple health-check endpoint.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Minimal health-check endpoint for uptime monitoring.

    Returns:
        JSON response with ``{"status": "ok"}``.
    """
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/projects/", include("apps.projects.urls", namespace="projects")),
    path("api/members/", include("apps.members.urls", namespace="members")),
    path("api/health/", health_check, name="health-check"),
]
