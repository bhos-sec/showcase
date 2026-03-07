/**
 * Custom React hook for fetching projects (The Forge).
 *
 * Handles data fetching, loading/error states, and caching.
 */

import { useEffect, useState } from "react";
import { fetchProjects } from "../services/projectService";
import type { Project, ApiError } from "../types/api";

interface UseProjectsState {
  projects: Project[];
  loading: boolean;
  error: ApiError | null;
  totalCount: number;
  hasNextPage: boolean;
  currentPage: number;
}

/**
 * Hook for fetching and managing projects.
 *
 * @param page - Current page number
 * @param pageSize - Items per page
 * @returns State object with projects and loading/error info
 */
export function useProjects(
  page: number = 1,
  pageSize: number = 25,
): UseProjectsState {
  const [state, setState] = useState<UseProjectsState>({
    projects: [],
    loading: true,
    error: null,
    totalCount: 0,
    hasNextPage: false,
    currentPage: page,
  });

  useEffect(() => {
    let isMounted = true; // Prevent state updates after unmount

    const loadProjects = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const response = await fetchProjects(page, pageSize);

        if (isMounted) {
          setState({
            projects: response.results,
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

    loadProjects();

    return () => {
      isMounted = false; // Cleanup on unmount
    };
  }, [page, pageSize]);

  return state;
}
