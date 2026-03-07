"""
Celery tasks for the projects module.

Defines periodic tasks that synchronise repository data from the
GitHub API into the local database.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="projects.sync_github_repos",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def sync_github_repos(self):
    """Synchronise all repositories from the GitHub organisation.

    This task is scheduled to run periodically via Celery Beat.
    On failure, it retries up to 3 times with a 60-second delay.

    Returns:
        Dictionary summary of the sync operation.
    """
    from apps.projects.services.github_service import GitHubRepoService

    try:
        service = GitHubRepoService()
        result = service.sync_repos()
        summary = {
            "created": result.created,
            "updated": result.updated,
            "errors": result.errors,
        }
        logger.info("sync_github_repos completed: %s", summary)
        return summary
    except Exception as exc:
        logger.exception("sync_github_repos failed, retrying...")
        raise self.retry(exc=exc)
