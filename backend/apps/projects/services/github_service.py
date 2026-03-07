"""
GitHub repository synchronisation service.

Fetches public repository data from the GitHub REST API for the
configured organisation and upserts Project and Language records
in the local database.

This service is the single source of truth for all GitHub ↔ Project
synchronisation logic, keeping it decoupled from Django models and
Celery tasks (Service Layer pattern).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx
from django.conf import settings

from apps.projects.models import Language, Project

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result summary of a repository sync operation.

    Attributes:
        created: Number of newly created projects.
        updated: Number of existing projects updated.
        errors: List of error messages encountered during sync.
    """

    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of projects processed successfully."""
        return self.created + self.updated


class GitHubRepoService:
    """Service for synchronising GitHub org repositories to local DB.

    Uses the GitHub REST API to fetch repository metadata and language
    breakdowns for all public repositories of the configured organisation.

    Args:
        org_name: GitHub organisation slug (default from settings).
        api_token: Personal access token for authenticated requests.
            Falls back to ``settings.GITHUB_API_TOKEN`` if not provided.
        timeout: HTTP request timeout in seconds.

    Example:
        >>> service = GitHubRepoService()
        >>> result = service.sync_repos()
        >>> print(f"Created {result.created}, updated {result.updated}")
    """

    PER_PAGE = 100  # GitHub maximum per-page for REST endpoints.

    def __init__(
        self,
        org_name: str | None = None,
        api_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._org = org_name or settings.GITHUB_ORG_NAME
        self._token = api_token or settings.GITHUB_API_TOKEN
        self._base_url = settings.GITHUB_API_BASE_URL
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers for GitHub API requests.

        Returns:
            Dictionary of headers including the auth token if available.
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _check_rate_limit(self, response: httpx.Response) -> None:
        """Log a warning when approaching the GitHub rate limit.

        Args:
            response: The HTTP response from a GitHub API call.
        """
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None and int(remaining) < 50:
            reset_ts = response.headers.get("X-RateLimit-Reset", "0")
            logger.warning(
                "GitHub rate limit low: %s remaining, resets at %s",
                remaining,
                datetime.fromtimestamp(int(reset_ts), tz=timezone.utc),
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_org_repos(self) -> list[dict]:
        """Fetch all public repositories for the organisation.

        Handles GitHub's paginated responses, iterating through all
        pages until no more results are returned.

        Returns:
            List of raw repository dictionaries from the GitHub API.

        Raises:
            httpx.HTTPStatusError: If any GitHub API call fails.
        """
        repos: list[dict] = []
        page = 1
        headers = self._build_headers()

        with httpx.Client(timeout=self._timeout) as client:
            while True:
                url = (
                    f"{self._base_url}/orgs/{self._org}/repos"
                    f"?type=public&per_page={self.PER_PAGE}&page={page}"
                )
                response = client.get(url, headers=headers)
                response.raise_for_status()
                self._check_rate_limit(response)

                batch = response.json()
                if not batch:
                    break

                repos.extend(batch)
                if len(batch) < self.PER_PAGE:
                    break
                page += 1

        logger.info("Fetched %d repositories from GitHub org '%s'.", len(repos), self._org)
        return repos

    def fetch_repo_languages(self, repo_full_name: str) -> dict[str, int]:
        """Fetch the language breakdown for a specific repository.

        Args:
            repo_full_name: Full name of the repo (e.g. "bhos-sec/lantern").

        Returns:
            Dictionary mapping language names to byte counts.

        Raises:
            httpx.HTTPStatusError: If the API call fails.
        """
        url = f"{self._base_url}/repos/{repo_full_name}/languages"
        headers = self._build_headers()

        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            self._check_rate_limit(response)
            return response.json()

    def sync_repos(self) -> SyncResult:
        """Synchronise all org repositories to the local database.

        For each repository fetched from GitHub:
        1. Upserts the ``Project`` record by ``github_id``.
        2. Fetches and upserts ``Language`` records.
        3. Updates the project's language associations.

        Returns:
            A ``SyncResult`` summarising created/updated counts and errors.
        """
        result = SyncResult()
        now = datetime.now(tz=timezone.utc)

        try:
            raw_repos = self.fetch_org_repos()
        except httpx.HTTPStatusError as exc:
            error_msg = f"Failed to fetch org repos: {exc}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            return result

        for repo_data in raw_repos:
            try:
                self._sync_single_repo(repo_data, now, result)
            except Exception as exc:
                error_msg = f"Error syncing repo '{repo_data.get('name', '?')}': {exc}"
                logger.exception(error_msg)
                result.errors.append(error_msg)

        logger.info(
            "Repo sync complete: created=%d, updated=%d, errors=%d",
            result.created,
            result.updated,
            len(result.errors),
        )
        return result

    # ------------------------------------------------------------------
    # Internal sync helpers
    # ------------------------------------------------------------------

    def _sync_single_repo(
        self, repo_data: dict, synced_at: datetime, result: SyncResult
    ) -> None:
        """Create or update a single Project from raw GitHub data.

        Args:
            repo_data: Raw repository dict from the GitHub API.
            synced_at: Timestamp to record as ``last_synced_at``.
            result: Mutable ``SyncResult`` to increment counters.
        """
        defaults = {
            "name": repo_data["name"],
            "description": repo_data.get("description") or "",
            "github_url": repo_data["html_url"],
            "homepage_url": repo_data.get("homepage") or "",
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "open_issues": repo_data.get("open_issues_count", 0),
            "last_synced_at": synced_at,
        }

        project, created = Project.objects.update_or_create(
            github_id=repo_data["id"],
            defaults=defaults,
        )

        if created:
            result.created += 1
        else:
            result.updated += 1

        # Sync languages for this repo.
        self._sync_languages(project, repo_data["full_name"])

    def _sync_languages(self, project: Project, full_name: str) -> None:
        """Fetch and associate languages for a project.

        Args:
            project: The ``Project`` instance to update.
            full_name: GitHub full repo name for the languages API call.
        """
        try:
            lang_data = self.fetch_repo_languages(full_name)
        except httpx.HTTPStatusError:
            logger.warning("Could not fetch languages for %s", full_name)
            return

        language_objects = []
        for lang_name in lang_data:
            lang_obj, _ = Language.objects.get_or_create(name=lang_name)
            language_objects.append(lang_obj)

        project.languages.set(language_objects)
