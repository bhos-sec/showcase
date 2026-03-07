"""
Celery application factory for the Showcase project.

This module configures the Celery instance, binds it to the Django
settings, and auto-discovers tasks from all installed apps.

Usage:
    The app is imported in config/__init__.py so that shared_task
    uses this app instance when workers start.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("showcase")

# Read config from Django settings, using the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task that prints the current request info."""
    print(f"Request: {self.request!r}")
