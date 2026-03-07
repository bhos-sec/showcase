/**
 * Custom React hook for fetching members (leaderboard).
 *
 * Handles data fetching, loading/error states, and pagination.
 */

import { useEffect, useState } from "react";
import { fetchMembers } from "../services/memberService";
import type { Member, ApiError } from "../types/api";

interface UseMembersState {
  members: Member[];
  loading: boolean;
  error: ApiError | null;
  totalCount: number;
  hasNextPage: boolean;
  currentPage: number;
}

/**
 * Hook for fetching and managing members/leaderboard.
 *
 * @param page - Current page number
 * @param pageSize - Items per page (default 25 matches backend)
 * @param tier - Optional tier filter
 * @returns State object with members and loading/error info
 */
export function useMembers(
  page: number = 1,
  pageSize: number = 25,
  tier?: string,
): UseMembersState {
  const [state, setState] = useState<UseMembersState>({
    members: [],
    loading: true,
    error: null,
    totalCount: 0,
    hasNextPage: false,
    currentPage: page,
  });

  useEffect(() => {
    let isMounted = true;

    const loadMembers = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const response = await fetchMembers(page, pageSize, tier);

        if (isMounted) {
          setState({
            members: response.results,
            loading: false,
            error: null,
            totalCount: response.count,
            hasNextPage: response.next !== null,
            currentPage: page,
          });
        }
      } catch (err) {
        if (isMounted) {
          const error = err as ApiError;
          setState((prev) => ({ ...prev, loading: false, error }));
        }
      }
    };

    loadMembers();

    return () => {
      isMounted = false;
    };
  }, [page, pageSize, tier]);

  return state;
}
