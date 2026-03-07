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
    from apps.members.models import Contribution, Member
    from apps.members.services.github_profile_service import GitHubProfileService

    logger.info("=" * 70)
    logger.info("🔄 STARTING: Member Contributions Synchronization")
    logger.info(f"   Task ID: {self.request.id}")
    logger.info(f"   Retry: {self.request.retries}/{self.max_retries}")
    logger.info("=" * 70)

    try:
        # Get current state
        active_members = Member.objects.filter(is_active=True).count()
        initial_contributions = Contribution.objects.count()
        logger.debug(f"Active members: {active_members}")
        logger.debug(f"Current contributions in DB: {initial_contributions}")

        # Sync contributions
        logger.info(f"Syncing contributions for {active_members} active members...")
        service = GitHubProfileService()
        results = service.sync_all_members()

        # Calculate statistics
        summary = {
            "members_synced": len(results),
            "total_created": sum(r.total_created for r in results),
            "total_errors": sum(len(r.errors) for r in results),
        }

        # Final state
        final_contributions = Contribution.objects.count()
        logger.info("-" * 70)
        logger.info("✅ COMPLETED: Member Contributions Synchronization")
        logger.info(f"   Members synced: {summary['members_synced']}")
        logger.info(f"   Contributions created: {summary['total_created']}")
        logger.info(f"   Errors: {summary['total_errors']}")
        logger.info(f"   Total contributions: {initial_contributions} → {final_contributions}")
        logger.info("=" * 70)

        return summary

    except Exception as exc:
        logger.error("=" * 70)
        logger.error("❌ FAILED: Member Contributions Synchronization")
        logger.error(f"   Task ID: {self.request.id}")
        logger.error(f"   Retry: {self.request.retries + 1}/{self.max_retries}")
        logger.exception("   Error details:")
        logger.error("=" * 70)
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
    from apps.members.models import Member
    from apps.members.services.scoring_service import ScoringService

    logger.info("=" * 70)
    logger.info("🔄 STARTING: Scores & Impact Recalculation")
    logger.info(f"   Task ID: {self.request.id}")
    logger.info(f"   Retry: {self.request.retries}/{self.max_retries}")
    logger.info("=" * 70)

    try:
        # Get current state
        members = Member.objects.filter(is_active=True)
        initial_count = members.count()
        logger.debug(f"Active members: {initial_count}")

        # Recalculate scores
        logger.info("Calculating merit scores for all members...")
        service = ScoringService()
        count = service.recalculate_all()

        # Show top members after recalculation
        top_members = Member.objects.filter(is_active=True).order_by("-score")[:5]
        logger.info("-" * 70)
        logger.info("✅ COMPLETED: Scores & Impact Recalculation")
        logger.info(f"   Members updated: {count}")
        logger.info("   Top 5 members:")
        for i, m in enumerate(top_members, 1):
            logger.info(f"      {i}. {m.name:20s} | Tier: {m.tier:8s} | Score: {m.score:6.0f} | Impact: {m.impact:3d}%")
        logger.info("=" * 70)

        summary = {"members_updated": count}
        return summary

    except Exception as exc:
        logger.error("=" * 70)
        logger.error("❌ FAILED: Scores & Impact Recalculation")
        logger.error(f"   Task ID: {self.request.id}")
        logger.error(f"   Retry: {self.request.retries + 1}/{self.max_retries}")
        logger.exception("   Error details:")
        logger.error("=" * 70)
        raise self.retry(exc=exc)


@shared_task(name="members.bootstrap_members")
def bootstrap_members():
    """Bootstrap Member records from the GitHub org's public member list.

    This task can be triggered manually to populate the initial
    member database from the organisation's GitHub membership.

    Returns:
        Dictionary with the number of new members created.
    """
    from apps.members.models import Member
    from apps.members.services.github_profile_service import GitHubProfileService

    logger.info("=" * 70)
    logger.info("🚀 STARTING: Bootstrap Members from GitHub Organization")
    logger.info("=" * 70)

    try:
        # Get current state
        initial_count = Member.objects.count()
        logger.debug(f"Current members in DB: {initial_count}")

        # Bootstrap
        logger.info("Fetching organization members from GitHub API...")
        service = GitHubProfileService()
        count = service.bootstrap_members_from_org()

        # Final state
        final_count = Member.objects.count()
        logger.info("-" * 70)
        logger.info("✅ COMPLETED: Bootstrap Members from GitHub Organization")
        logger.info(f"   Members created: {count}")
        logger.info(f"   Total members: {initial_count} → {final_count}")

        # Show newly created members
        new_members = Member.objects.filter(is_active=True).order_by("-created_at")[:min(count, 5)]
        if new_members:
            logger.info("   Recently added members:")
            for m in new_members:
                logger.info(f"      • {m.name} (@{m.github_username})")

        logger.info("=" * 70)
        return {"members_created": count}

    except Exception as exc:
        logger.error("=" * 70)
        logger.error("❌ FAILED: Bootstrap Members from GitHub Organization")
        logger.exception("   Error details:")
        logger.error("=" * 70)
        raise
