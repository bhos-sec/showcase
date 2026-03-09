import { getBadgeConfig, getBadgeColorClass } from "../constants/badges";

interface BadgeItemProps {
  name: string;
  size?: "sm" | "md" | "lg";
  showTooltip?: boolean;
}

/**
 * Badge Component
 *
 * Renders a single badge with icon and optional tooltip.
 * Automatically looks up badge configuration from the registry.
 */
export function BadgeItem({
  name,
  size = "md",
  showTooltip = true,
}: BadgeItemProps) {
  const config = getBadgeConfig(name);

  if (!config) {
    // Fallback for unknown badges
    return (
      <span
        className="flex items-center gap-1 px-1 py-0.5 md:px-1.5 md:py-0.5 text-[8px] md:text-[9px] uppercase tracking-widest font-mono border border-border bg-background text-muted-foreground whitespace-nowrap"
        title={name}
      >
        {name}
      </span>
    );
  }

  const Icon = config.icon;
  const colorClass = getBadgeColorClass(name);

  const sizeClasses = {
    sm: "w-2 h-2 md:w-2.5 md:h-2.5",
    md: "w-2.5 h-2.5 md:w-3 md:h-3",
    lg: "w-3 h-3 md:w-4 md:h-4",
  };

  return (
    <span
      className="flex items-center gap-1 px-1 py-0.5 md:px-1.5 md:py-0.5 text-[8px] md:text-[9px] uppercase tracking-widest font-mono border border-border bg-background text-muted-foreground hover:bg-secondary/50 transition-colors whitespace-nowrap cursor-help"
      title={showTooltip ? `${name}: ${config.description}` : name}
    >
      <Icon className={`${sizeClasses[size]} ${colorClass}`} />
      {name}
    </span>
  );
}

interface BadgeListProps {
  badges: string[];
  maxDisplay?: number;
  size?: "sm" | "md" | "lg";
}

/**
 * Badge List Component
 *
 * Renders multiple badges with optional truncation.
 */
export function BadgeList({ badges, maxDisplay, size = "md" }: BadgeListProps) {
  if (!badges || badges.length === 0) {
    return null;
  }

  const displayBadges = maxDisplay ? badges.slice(0, maxDisplay) : badges;
  const hiddenCount =
    maxDisplay && badges.length > maxDisplay ? badges.length - maxDisplay : 0;

  return (
    <div className="flex flex-wrap gap-1 md:gap-2">
      {displayBadges.map((badge) => (
        <BadgeItem key={badge} name={badge} size={size} />
      ))}
      {hiddenCount > 0 && (
        <span
          className="flex items-center gap-1 px-1 py-0.5 md:px-1.5 md:py-0.5 text-[8px] md:text-[9px] uppercase tracking-widest font-mono border border-dashed border-border bg-background text-muted-foreground whitespace-nowrap"
          title={`${hiddenCount} more badge${hiddenCount > 1 ? "s" : ""}`}
        >
          +{hiddenCount}
        </span>
      )}
    </div>
  );
}
