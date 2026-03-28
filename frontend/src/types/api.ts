/**
 * API Type Definitions
 *
 * Strongly-typed interfaces matching the Django backend API responses.
 * These ensure type safety across the entire frontend application.
 */

/**
 * Paginated API response wrapper.
 * All list endpoints return this structure.
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Project from the Forge API (/api/projects/).
 */
export interface Project {
  id: number;
  name: string;
  description: string;
  stars: number;
  forks: number;
  open_issues: number;
  languages: string[];
  status: "Active" | "Beta" | "Alpha";
  github_url: string;
  homepage_url: string;
}

/**
 * Member from the Leaderboard API (/api/members/).
 */
export interface Member {
  id: number;
  name: string;
  tier: "Founder" | "Lead" | "Mentor" | "Member" | "Learner";
  score: string; // Decimal from Django
  monthly_score: string; // Decimal from Django
  weekly_score: string; // Decimal from Django
  github: string;
  contributions: number;
  monthly_contribution_count: number;
  weekly_contribution_count: number;
  impact: number; // 0-100 percentile
  additions: number; // Total lines added
  deletions: number; // Total lines deleted
  badges: string[];
  avatar: string;
}

/**
 * Member detail with contributions breakdown (/api/members/<id>/).
 */
export interface MemberDetail extends Member {
  recent_contributions: Contribution[];
  contribution_breakdown: Record<string, number>;
}

/**
 * Individual contribution record.
 */
export interface Contribution {
  id: number;
  contribution_type: string;
  type_display: string;
  title: string;
  url: string;
  repository_name: string | null;
  points: string;
  additions: number;
  deletions: number;
  occurred_at: string;
}

/**
 * API error response.
 */
export interface ApiError {
  message: string;
  status: number;
}
