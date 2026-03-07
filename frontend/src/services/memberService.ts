/**
 * Member API Service
 *
 * Service layer for Member/Leaderboard API calls.
 */

import { apiClient } from "./api";
import type { Member, MemberDetail, PaginatedResponse } from "../types/api";

/**
 * Fetch a paginated list of members (leaderboard).
 *
 * @param page - Page number (1-indexed)
 * @param pageSize - Items per page
 * @param tier - Optional filter by tier
 * @returns Paginated list of members
 */
export async function fetchMembers(
  page: number = 1,
  pageSize: number = 25,
  tier?: string,
): Promise<PaginatedResponse<Member>> {
  const params: Record<string, string | number> = {
    page,
    page_size: pageSize,
  };

  if (tier) {
    params.tier = tier;
  }

  return apiClient.get<PaginatedResponse<Member>>("/members/", params);
}

/**
 * Fetch a single member by ID with full details.
 *
 * @param id - Member ID
 * @returns Member details including recent contributions
 */
export async function fetchMember(id: number): Promise<MemberDetail> {
  return apiClient.get<MemberDetail>(`/members/${id}/`);
}
