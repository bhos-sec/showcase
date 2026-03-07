/**
 * Utility Functions
 *
 * Common utility functions used across components.
 */

/**
 * Format a score as a decimal string.
 *
 * @param score - Score value (could be string or number)
 * @returns Formatted score string
 */
export function formatScore(score: string | number): string {
  const numScore = typeof score === "string" ? parseFloat(score) : score;
  return numScore.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Truncate text to a maximum length with ellipsis.
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated string
 */
export function truncateText(text: string, maxLength: number): string {
  return text.length > maxLength ? `${text.slice(0, maxLength - 3)}...` : text;
}

/**
 * Format a number as a localized string.
 *
 * @param num - Number to format
 * @returns Formatted number
 */
export function formatNumber(num: number): string {
  return num.toLocaleString("en-US");
}
