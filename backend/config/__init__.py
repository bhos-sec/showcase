"""
Config package for the Showcase Django project.

Import the Celery app so that shared_task will use it automatically
when Django starts.
"""

from .celery import app as celery_app

__all__ = ["celery_app"]
