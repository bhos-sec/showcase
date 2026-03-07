"""URL configuration for the members module."""

from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("", views.MemberLeaderboardView.as_view(), name="member-list"),
    path("<int:pk>/", views.MemberDetailView.as_view(), name="member-detail"),
]
