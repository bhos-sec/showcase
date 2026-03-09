/**
 * Badge Configuration System
 *
 * Defines all available badges with their metadata and display properties.
 * This is the single source of truth for badge information in the frontend.
 */

import {
  Shield,
  Star,
  Award,
  Zap,
  Users,
  Megaphone,
  Flame,
  Rocket,
  Sparkles,
  LucideIcon,
} from "lucide-react";

export interface BadgeConfig {
  name: string;
  description: string;
  icon: LucideIcon;
  color: "purple" | "amber" | "blue" | "accent" | "green" | "pink" | "orange";
}

export const BADGE_REGISTRY: Record<string, BadgeConfig> = {
  Architect: {
    name: "Architect",
    description: "Designed a major system or feature.",
    icon: Shield,
    color: "purple",
  },
  Visionary: {
    name: "Visionary",
    description: "Proposed an accepted strategic initiative.",
    icon: Star,
    color: "amber",
  },
  Reviewer: {
    name: "Reviewer",
    description: "Completed 50+ code reviews.",
    icon: Award,
    color: "blue",
  },
  Optimizer: {
    name: "Optimizer",
    description: "Significantly improved performance.",
    icon: Zap,
    color: "accent",
  },
  Guide: {
    name: "Guide",
    description: "Mentored a new member through onboarding.",
    icon: Users,
    color: "green",
  },
  Speaker: {
    name: "Speaker",
    description: "Presented at a collective session.",
    icon: Megaphone,
    color: "pink",
  },
  Hacker: {
    name: "Hacker",
    description: "Won or placed in a hackathon.",
    icon: Flame,
    color: "orange",
  },
  "Fast Learner": {
    name: "Fast Learner",
    description: "Completed a learning track ahead of schedule.",
    icon: Rocket,
    color: "accent",
  },
  Newcomer: {
    name: "Newcomer",
    description: "Made first contribution to the collective.",
    icon: Sparkles,
    color: "blue",
  },
};

const BADGE_COLOR_TO_TAILWIND: Record<BadgeConfig["color"], string> = {
  purple: "text-purple-400",
  amber: "text-amber-400",
  blue: "text-blue-400",
  accent: "text-accent",
  green: "text-green-400",
  pink: "text-pink-400",
  orange: "text-orange-400",
};

/**
 * Get badge configuration by name
 * @param badgeName - The name of the badge
 * @returns Badge configuration or undefined if not found
 */
export function getBadgeConfig(badgeName: string): BadgeConfig | undefined {
  return BADGE_REGISTRY[badgeName];
}

/**
 * Get Tailwind color class for a badge
 * @param badgeName - The name of the badge
 * @returns Tailwind color class
 */
export function getBadgeColorClass(badgeName: string): string {
  const config = getBadgeConfig(badgeName);
  return config
    ? BADGE_COLOR_TO_TAILWIND[config.color]
    : BADGE_COLOR_TO_TAILWIND.blue;
}

/**
 * Get all available badges
 * @returns Array of badge configurations
 */
export function getAllBadges(): BadgeConfig[] {
  return Object.values(BADGE_REGISTRY);
}
