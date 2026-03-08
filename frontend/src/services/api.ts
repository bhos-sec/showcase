/// <reference types="vite/client" />

/**
 * API Configuration and Base Service
 *
 * Centralized configuration for API endpoints and a base client
 * for all API communication.
 */

import type { ApiError } from "../types/api";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

/**
 * Generic API client for making HTTP requests to the backend.
 * Handles error responses and type-safe JSON parsing.
 */
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make a GET request to the API.
   *
   * @param endpoint - The API endpoint path (e.g., "/projects/")
   * @param params - Optional query parameters
   * @returns Parsed JSON response
   * @throws ApiError if the request fails
   */
  async get<T>(
    endpoint: string,
    params?: Record<string, string | number>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error: ApiError = {
        status: response.status,
        message: `HTTP ${response.status}: ${response.statusText}`,
      };
      throw error;
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
