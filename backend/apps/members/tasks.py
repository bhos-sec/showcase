"""
Celery tasks for the members module.

Defines periodic tasks that synchronise member contribution data
from GitHub and recalculate merit scores.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="members.sync_member_contributions",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
)
def sync_member_contributions(self):
    """Synchronise contribution data for all active members.

    Fetches PRs, reviews, and issues from the GitHub API and
    creates local Contribution records. Scheduled to run every
    6 hours via Celery Beat.

    Returns:
        Summary dictionary with sync statistics.
    """
    from apps.members.services.github_profile_service import GitHubProfileService

    try:
        service = GitHubProfileService()
        results = service.sync_all_members()
        summary = {
            "members_synced": len(results),
            "total_created": sum(r.total_created for r in results),
            "total_errors": sum(len(r.errors) for r in results),
        }
        logger.info("sync_member_contributions completed: %s", summary)
        return summary
    except Exception as exc:
        logger.exception("sync_member_contributions failed, retrying...")
        raise self.retry(exc=exc)


@shared_task(
    name="members.recalculate_all_scores",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def recalculate_all_scores(self):
    """Recalculate merit scores and impact for all active members.

    Should be triggered after contribution sync completes.

    Returns:
        Dictionary with the number of members updated.
    """
    from apps.members.services.scoring_service import ScoringService

    try:
        service = ScoringService()
        count = service.recalculate_all()
        summary = {"members_updated": count}
        logger.info("recalculate_all_scores completed: %s", summary)
        return summary
    except Exception as exc:
        logger.exception("recalculate_all_scores failed, retrying...")
        raise self.retry(exc=exc)


@shared_task(name="members.bootstrap_members")
def bootstrap_members():
    """Bootstrap Member records from the GitHub org's public member list.

    This task can be triggered manually to populate the initial
    member database from the organisation's GitHub membership.

    Returns:
        Dictionary with the number of new members created.
    """
    from apps.members.services.github_profile_service import GitHubProfileService

    service = GitHubProfileService()
    count = service.bootstrap_members_from_org()
    return {"members_created": count}
