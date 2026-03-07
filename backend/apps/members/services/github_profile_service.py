"""
GitHub profile and contribution synchronisation service.

Aggregates contribution data for collective members using the GitHub
GraphQL API for efficient bulk queries, with REST API fallback for
detailed contribution record creation.

Architecture:
    GitHubProfileService
        ├── fetch_org_members() — list members from the org
        ├── fetch_member_stats() — GraphQL contribution summary
        ├── fetch_member_prs() — REST: merged PRs
        ├── fetch_member_reviews() — REST: code reviews
        ├── fetch_member_issues() — REST: closed issues
        ├── sync_member() — orchestrate sync for one member
        └── sync_all_members() — orchestrate sync for all members
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx
from django.conf import settings
from django.utils import timezone as dj_timezone

from apps.members.models import Member
from apps.members.services.contribution_factory import ContributionFactory

logger = logging.getLogger(__name__)


@dataclass
class MemberSyncResult:
    """Result summary for syncing a single member's contributions.

    Attributes:
        username: GitHub username of the member.
        prs_created: Number of new PR contribution records.
        reviews_created: Number of new review contribution records.
        issues_created: Number of new issue contribution records.
        errors: List of error messages.
    """

    username: str = ""
    prs_created: int = 0
    reviews_created: int = 0
    issues_created: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_created(self) -> int:
        """Total new contributions created."""
        return self.prs_created + self.reviews_created + self.issues_created


class GitHubProfileService:
    """Service for syncing member contribution data from GitHub.

    Uses the GitHub GraphQL API for efficient contribution summaries
    and the REST Search API for detailed contribution records (PRs,
    reviews, issues) that are stored locally.

    Args:
        api_token: GitHub Personal Access Token. Falls back to
            ``settings.GITHUB_API_TOKEN`` if not provided.
        org_name: GitHub organisation slug. Falls back to
            ``settings.GITHUB_ORG_NAME``.
        timeout: HTTP request timeout in seconds.

    Example:
        >>> service = GitHubProfileService()
        >>> results = service.sync_all_members()
        >>> print(f"Synced {len(results)} members")
    """

    RATE_LIMIT_PAUSE = 2.0  # Seconds to pause between members to respect limits.

    def __init__(
        self,
        api_token: str | None = None,
        org_name: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._token = api_token or settings.GITHUB_API_TOKEN
        self._org = org_name or settings.GITHUB_ORG_NAME
        self._base_url = settings.GITHUB_API_BASE_URL
        self._graphql_url = settings.GITHUB_GRAPHQL_URL
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rest_headers(self) -> dict[str, str]:
        """Build HTTP headers for REST API requests.

        Returns:
            Headers dict with auth and API versioning.
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _graphql_headers(self) -> dict[str, str]:
        """Build HTTP headers for GraphQL API requests.

        Returns:
            Headers dict with auth for GraphQL endpoint.
        """
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    # ------------------------------------------------------------------
    # Public API — Data fetching
    # ------------------------------------------------------------------

    def fetch_org_members(self) -> list[dict]:
        """Fetch all public members of the organisation.

        Returns:
            List of member dicts with ``login``, ``avatar_url``, etc.

        Raises:
            httpx.HTTPStatusError: If the API call fails.
        """
        members: list[dict] = []
        page = 1
        headers = self._rest_headers()

        with httpx.Client(timeout=self._timeout) as client:
            while True:
                url = (
                    f"{self._base_url}/orgs/{self._org}/members"
                    f"?per_page=100&page={page}"
                )
                response = client.get(url, headers=headers)
                response.raise_for_status()

                batch = response.json()
                if not batch:
                    break
                members.extend(batch)
                if len(batch) < 100:
                    break
                page += 1

        logger.info("Fetched %d members from org '%s'.", len(members), self._org)
        return members

    def fetch_member_stats_graphql(self, username: str) -> dict:
        """Fetch contribution summary via the GitHub GraphQL API.

        Uses the ``contributionsCollection`` query to get aggregate
        counts in a single request per member.

        Args:
            username: GitHub username to query.

        Returns:
            Dictionary with keys: ``totalCommitContributions``,
            ``totalPullRequestContributions``,
            ``totalPullRequestReviewContributions``,
            ``totalIssueContributions``.
        """
        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              totalIssueContributions
            }
          }
        }
        """

        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                self._graphql_url,
                json={"query": query, "variables": {"username": username}},
                headers=self._graphql_headers(),
            )
            response.raise_for_status()
            data = response.json()

        user_data = data.get("data", {}).get("user")
        if not user_data:
            logger.warning("No GraphQL data returned for user '%s'.", username)
            return {}

        return user_data.get("contributionsCollection", {})

    def fetch_member_prs(
        self,
        username: str,
        since: datetime | None = None,
    ) -> list[dict]:
        """Fetch merged pull requests by a member in the org's repos.

        Args:
            username: GitHub username.
            since: Optional cutoff date — only fetch PRs merged after this.

        Returns:
            List of PR dicts from the GitHub Search API.
        """
        date_filter = ""
        if since:
            date_filter = f"+merged:>={since.strftime('%Y-%m-%d')}"

        query = f"type:pr+author:{username}+org:{self._org}+is:merged{date_filter}"
        return self._search_issues(query)

    def fetch_member_issues(
        self,
        username: str,
        since: datetime | None = None,
    ) -> list[dict]:
        """Fetch closed issues assigned to a member in the org's repos.

        Args:
            username: GitHub username.
            since: Optional cutoff date.

        Returns:
            List of issue dicts from the GitHub Search API.
        """
        date_filter = ""
        if since:
            date_filter = f"+closed:>={since.strftime('%Y-%m-%d')}"

        query = f"type:issue+assignee:{username}+org:{self._org}+is:closed{date_filter}"
        return self._search_issues(query)

    def _search_issues(self, query: str) -> list[dict]:
        """Execute a GitHub Search API query for issues/PRs.

        Handles pagination and rate limit headers.

        Args:
            query: URL-encoded search query string.

        Returns:
            List of item dicts from search results.
        """
        items: list[dict] = []
        page = 1
        headers = self._rest_headers()

        with httpx.Client(timeout=self._timeout) as client:
            while True:
                url = (
                    f"{self._base_url}/search/issues"
                    f"?q={query}&per_page=100&page={page}"
                )
                response = client.get(url, headers=headers)

                # Handle search rate limit (30 req/min).
                if response.status_code == 403:
                    logger.warning("Search rate limit hit; pausing 60s.")
                    time.sleep(60)
                    continue

                response.raise_for_status()
                data = response.json()
                batch = data.get("items", [])
                items.extend(batch)

                if len(items) >= data.get("total_count", 0) or not batch:
                    break
                page += 1

        return items

    def _enrich_pr_with_stats(self, pr_data: dict) -> dict:
        """Fetch and add additions/deletions to PR data from search results.

        The Search API doesn't include these fields, so we fetch them from
        the direct PR endpoint if available.

        Args:
            pr_data: PR data from the Search API.

        Returns:
            PR data dict enriched with additions and deletions.
        """
        try:
            # Search API returns issues URL, but for PRs we need to convert to /pulls/ endpoint
            # https://api.github.com/repos/OWNER/REPO/issues/NUMBER -> /pulls/NUMBER
            url = pr_data.get("url", "")
            if url and "/issues/" in url:
                # Convert issues URL to pulls URL for PR data
                pr_url = url.replace("/issues/", "/pulls/")
            else:
                pr_url = pr_data.get("pull_request_url") or url
            
            if pr_url:
                logger.debug("Fetching PR stats from: %s", pr_url)
                headers = self._rest_headers()
                
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.get(pr_url, headers=headers)
                    response.raise_for_status()
                    pr_details = response.json()
                    
                    # Add line stats from detailed endpoint
                    additions = pr_details.get("additions", 0)
                    deletions = pr_details.get("deletions", 0)
                    pr_data["additions"] = additions
                    pr_data["deletions"] = deletions
                    logger.debug("PR %s: +%d -%d", pr_data.get("number"), additions, deletions)
            else:
                logger.warning("PR data missing URL: %s", pr_data)
                pr_data.setdefault("additions", 0)
                pr_data.setdefault("deletions", 0)
        except Exception as exc:
            logger.warning("Failed to fetch PR stats for %s: %s", pr_data.get("url"), exc)
            # Fallback to 0 if fetch fails
            pr_data.setdefault("additions", 0)
            pr_data.setdefault("deletions", 0)
        
        return pr_data

    def _enrich_commit_with_stats(self, commit_data: dict) -> dict:
        """Fetch and add additions/deletions to commit data.

        Fetches detailed commit info from the direct commit endpoint.

        Args:
            commit_data: Commit data dict.

        Returns:
            Commit data dict enriched with additions and deletions.
        """
        try:
            if "url" in commit_data:
                url = commit_data["url"]
                headers = self._rest_headers()
                
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    commit_details = response.json()
                    
                    # Add line stats from detailed endpoint
                    commit_data["additions"] = commit_details.get("stats", {}).get("additions", 0)
                    commit_data["deletions"] = commit_details.get("stats", {}).get("deletions", 0)
        except Exception as exc:
            logger.warning("Failed to fetch commit stats for %s: %s", commit_data.get("url"), exc)
            # Fallback to 0 if fetch fails
            commit_data.setdefault("additions", 0)
            commit_data.setdefault("deletions", 0)
        
        return commit_data

    # ------------------------------------------------------------------
    # Public API — Sync orchestration
    # ------------------------------------------------------------------

    def sync_member(self, member: Member) -> MemberSyncResult:
        """Synchronise contribution data for a single member.

        Fetches PRs and issues from the GitHub Search API and creates
        contribution records via the ContributionFactory.

        Args:
            member: The Member instance to sync.

        Returns:
            A MemberSyncResult with counts of created records.
        """
        result = MemberSyncResult(username=member.github_username)
        username = member.github_username

        # Update avatar from GitHub profile.
        try:
            self._update_avatar(member)
        except Exception as exc:
            result.errors.append(f"Avatar update failed: {exc}")

        # Fetch and create PR contributions.
        try:
            prs = self.fetch_member_prs(username)
            for pr_data in prs:
                # Enrich with additions/deletions from PR detail endpoint
                pr_data = self._enrich_pr_with_stats(pr_data)
                _, created = ContributionFactory.create_from_pull_request(
                    member=member, pr_data=pr_data
                )
                if created:
                    result.prs_created += 1
        except Exception as exc:
            error_msg = f"PR sync failed for {username}: {exc}"
            logger.exception(error_msg)
            result.errors.append(error_msg)

        # Fetch and create issue contributions.
        try:
            issues = self.fetch_member_issues(username)
            for issue_data in issues:
                _, created = ContributionFactory.create_from_issue(
                    member=member, issue_data=issue_data
                )
                if created:
                    result.issues_created += 1
        except Exception as exc:
            error_msg = f"Issue sync failed for {username}: {exc}"
            logger.exception(error_msg)
            result.errors.append(error_msg)

        logger.info(
            "Synced member '%s': prs=%d, issues=%d, errors=%d",
            username,
            result.prs_created,
            result.issues_created,
            len(result.errors),
        )
        return result

    def sync_all_members(self) -> list[MemberSyncResult]:
        """Synchronise contributions for all active members.

        Iterates through all active members, syncing each with a
        pause between requests to respect GitHub rate limits.

        Returns:
            List of MemberSyncResult for each synced member.
        """
        members = Member.objects.filter(is_active=True)
        results: list[MemberSyncResult] = []

        for member in members:
            result = self.sync_member(member)
            results.append(result)
            time.sleep(self.RATE_LIMIT_PAUSE)

        total_created = sum(r.total_created for r in results)
        total_errors = sum(len(r.errors) for r in results)
        logger.info(
            "Full member sync complete: %d members, %d new contributions, %d errors.",
            len(results),
            total_created,
            total_errors,
        )
        return results

    def bootstrap_members_from_org(self) -> int:
        """Create Member records from the GitHub org's member list.

        Fetches all public org members and creates local Member
        records for any that don't already exist.

        Returns:
            Number of new members created.
        """
        org_members = self.fetch_org_members()
        created_count = 0

        for gm in org_members:
            _, created = Member.objects.get_or_create(
                github_username=gm["login"],
                defaults={
                    "name": gm.get("login", ""),
                    "avatar_url": gm.get("avatar_url", ""),
                },
            )
            if created:
                created_count += 1

        logger.info("Bootstrapped %d new members from org '%s'.", created_count, self._org)
        return created_count

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _update_avatar(self, member: Member) -> None:
        """Update a member's avatar URL from their GitHub profile.

        Args:
            member: The Member instance to update.
        """
        url = f"{self._base_url}/users/{member.github_username}"
        headers = self._rest_headers()

        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            profile = response.json()

        avatar = profile.get("avatar_url", "")
        name = profile.get("name") or profile.get("login", member.name)

        if avatar and avatar != member.avatar_url:
            member.avatar_url = avatar
        if name and name != member.name:
            member.name = name
        member.save(update_fields=["avatar_url", "name", "updated_at"])
