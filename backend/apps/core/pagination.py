"""
Custom DRF pagination classes for the Showcase project.

Provides a standardised pagination style used across all list endpoints,
matching the frontend's expectation of 25 items per page.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Page-number based pagination with configurable page size.

    Default page size is 25 (matching the frontend leaderboard).
    Clients may override via the ``page_size`` query parameter up
    to a maximum of 100.

    Query Parameters:
        page: The page number (1-indexed).
        page_size: Number of results per page (max 100).
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
