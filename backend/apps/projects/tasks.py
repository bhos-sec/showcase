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
    from apps.projects.models import Project
    from apps.projects.services.github_service import GitHubRepoService

    logger.info("=" * 70)
    logger.info("🔄 STARTING: GitHub Repository Synchronization")
    logger.info(f"   Task ID: {self.request.id}")
    logger.info(f"   Retry: {self.request.retries}/{self.max_retries}")
    logger.info("=" * 70)

    try:
        # Get current state
        initial_count = Project.objects.count()
        logger.debug(f"Current projects in DB: {initial_count}")

        # Sync repos
        logger.info("Fetching repositories from GitHub API...")
        service = GitHubRepoService()
        result = service.sync_repos()

        # Build summary
        summary = {
            "created": result.created,
            "updated": result.updated,
            "errors": result.errors,
        }

        # Final state
        final_count = Project.objects.count()
        logger.info("-" * 70)
        logger.info("✅ COMPLETED: GitHub Repository Synchronization")
        logger.info(f"   Created: {result.created}")
        logger.info(f"   Updated: {result.updated}")
        logger.info(f"   Errors: {result.errors}")
        logger.info(f"   Total projects: {initial_count} → {final_count}")
        logger.info("=" * 70)

        return summary

    except Exception as exc:
        logger.error("=" * 70)
        logger.error("❌ FAILED: GitHub Repository Synchronization")
        logger.error(f"   Task ID: {self.request.id}")
        logger.error(f"   Retry: {self.request.retries + 1}/{self.max_retries}")
        logger.exception("   Error details:")
        logger.error("=" * 70)
        raise self.retry(exc=exc) from exc
