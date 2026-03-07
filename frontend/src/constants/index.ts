/**
 * Application Constants
 *
 * Shared constants used across the application.
 */

export const PROJECTS_PER_PAGE = 25;
export const MEMBERS_PER_PAGE = 25;
export const INITIAL_PROJECTS_SHOWN = 3;

export const TIER_COLORS = {
  Founder: {
    color: "text-purple-400",
    bg: "bg-purple-400/10",
    border: "border-purple-400/30",
  },
  Lead: {
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-400/30",
  },
  Mentor: {
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    border: "border-blue-400/30",
  },
  Member: {
    color: "text-[var(--color-bhos-mint)]",
    bg: "bg-[var(--color-bhos-mint-dim)]",
    border: "border-[var(--color-bhos-mint)]/30",
  },
  Learner: {
    color: "text-slate-400",
    bg: "bg-slate-400/10",
    border: "border-slate-400/30",
  },
} as const;

export const PROJECT_STATUS_COLORS = {
  Active: "bg-green-500/20 text-green-300 border-green-500/40",
  Beta: "bg-amber-500/20 text-amber-300 border-amber-500/40",
  Alpha: "bg-blue-500/20 text-blue-300 border-blue-500/40",
} as const;
