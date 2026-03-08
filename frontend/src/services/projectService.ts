/**
 * Project API Service
 *
 * Service layer for Project-related API calls (The Forge).
 */

import { apiClient } from "./api";
import type { Project, PaginatedResponse } from "../types/api";

/**
 * Fetch a paginated list of projects.
 *
 * @param page - Page number (1-indexed)
 * @param pageSize - Items per page
 * @param status - Optional filter by project status
 * @returns Paginated list of projects
 */
export async function fetchProjects(
  page: number = 1,
  pageSize: number = 25,
  status?: string
): Promise<PaginatedResponse<Project>> {
  const params: Record<string, string | number> = {
    page,
    page_size: pageSize,
  };

  if (status) {
    params.status = status;
  }

  return apiClient.get<PaginatedResponse<Project>>("/projects/", params);
}

/**
 * Fetch a single project by ID.
 *
 * @param id - Project ID
 * @returns Project details
 */
export async function fetchProject(id: number): Promise<Project> {
  return apiClient.get<Project>(`/projects/${id}/`);
}
