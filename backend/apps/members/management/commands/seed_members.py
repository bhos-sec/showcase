"""
Management command to bootstrap members from the GitHub organisation.

Usage:
    python manage.py seed_members
    python manage.py seed_members --sync  # Also sync contributions
"""

from django.core.management.base import BaseCommand

from apps.members.services.github_profile_service import GitHubProfileService
from apps.members.services.scoring_service import ScoringService


class Command(BaseCommand):
    """Bootstrap member records from the GitHub org's public member list."""

    help = (
        "Fetch all public members from the GitHub organisation and "
        "create local Member records. Optionally sync contributions "
        "and recalculate scores."
    )

    def add_arguments(self, parser):
        """Add custom CLI arguments.

        Args:
            parser: The argparse parser instance.
        """
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Also sync contributions and recalculate scores after bootstrapping.",
        )

    def handle(self, *args, **options):
        """Execute the command.

        Args:
            *args: Positional arguments (unused).
            **options: Parsed CLI options.
        """
        self.stdout.write("Bootstrapping members from GitHub org...")

        service = GitHubProfileService()
        count = service.bootstrap_members_from_org()
        self.stdout.write(self.style.SUCCESS(f"Created {count} new members."))

        if options["sync"]:
            self.stdout.write("Syncing contributions for all members...")
            results = service.sync_all_members()
            total = sum(r.total_created for r in results)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {total} new contributions across {len(results)} members."
                )
            )

            self.stdout.write("Recalculating scores...")
            scoring = ScoringService()
            updated = scoring.recalculate_all()
            self.stdout.write(
                self.style.SUCCESS(f"Updated scores for {updated} members.")
            )

        self.stdout.write(self.style.SUCCESS("Done."))
