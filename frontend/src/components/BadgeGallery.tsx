import { getAllBadges } from "../constants/badges";
import { BadgeItem } from "./Badge";

/**
 * Badge Gallery Component
 *
 * Showcases all available badge definitions and their metadata.
 * Useful for documentation, testing, and badge administration.
 */
export function BadgeGallery() {
  const badges = getAllBadges();

  return (
    <div className="w-full">
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-lg md:text-xl font-bold tracking-tighter text-foreground uppercase mb-4">
            Available Badges
          </h3>
          <p className="text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-wider mb-6">
            [ TOTAL_BADGES: {badges.length} ]
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {badges.map((badge) => (
            <div
              key={badge.name}
              className="p-4 border border-border bg-secondary/5 hover:bg-secondary/10 transition-colors"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div>
                  <h4 className="text-xs md:text-sm font-bold text-foreground uppercase tracking-tight">
                    {badge.name}
                  </h4>
                  <p className="text-[8px] md:text-[9px] text-muted-foreground mt-1">
                    {badge.description}
                  </p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border/50">
                <BadgeItem name={badge.name} size="md" showTooltip={true} />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 p-4 border border-dashed border-border/50 bg-background text-muted-foreground text-[8px] md:text-[9px] font-mono uppercase tracking-wider">
          <p className="mb-2">To add a new badge:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Add a migration to seed the badge in Django</li>
            <li>Add badge config to BADGE_REGISTRY in constants/badges.ts</li>
            <li>Assign badges to members via Django admin</li>
            <li>Badges will automatically appear on leaderboard</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
