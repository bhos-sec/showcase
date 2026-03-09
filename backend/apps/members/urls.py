"""URL configuration for the members module."""

from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("", views.MemberLeaderboardView.as_view(), name="member-list"),
    path("<int:pk>/", views.MemberDetailView.as_view(), name="member-detail"),
    # path("public/", views.LeaderboardHTMLView.as_view(), name="leaderboard-public"),
    # path("leaderboard-table/", views.LeaderboardTableView.as_view(), name="leaderboard-table"),
    path("leaderboard-image/", views.LeaderboardImageView.as_view(), name="leaderboard-image"),
]
