"""
Custom DRF permissions for the Showcase project.

These permissions enforce access control across the API, ensuring
that write operations are restricted to admin users while read
access remains public.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(BasePermission):
    """Allow unrestricted read access; restrict writes to staff users.

    Safe HTTP methods (GET, HEAD, OPTIONS) are allowed for any request.
    All other methods require the request user to be authenticated and
    have ``is_staff`` set to ``True``.

    Example:
        Use on a ViewSet to allow public list/retrieve but admin-only
        create/update/delete::

            class ProjectViewSet(ModelViewSet):
                permission_classes = [IsAdminOrReadOnly]
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request should be permitted.

        Args:
            request: The incoming DRF request.
            view: The view being accessed.

        Returns:
            True if the method is safe or the user is staff, False otherwise.
        """
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
