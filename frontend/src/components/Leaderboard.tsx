import {
  Trophy,
  Github,
  Star,
  Shield,
  Award,
  Zap,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import { useMembers } from "../hooks";
import { MEMBERS_PER_PAGE, TIER_COLORS } from "../constants";

const TIER_BAR_COLORS = {
  Founder: "rgb(192, 132, 250)", // purple-400
  Lead: "rgb(251, 191, 36)", // amber-400
  Mentor: "rgb(96, 165, 250)", // blue-400
  Member: "rgb(0, 255, 166)", // mint
  Learner: "rgb(148, 163, 184)", // slate-400
} as const;

function Counter({ value }: { value: number | string }) {
  const numValue = typeof value === "string" ? parseInt(value) : value;
  return <span>{numValue.toLocaleString()}</span>;
}

export function Leaderboard() {
  const [currentPage, setCurrentPage] = useState(1);
  const { members, loading, error, totalCount, hasNextPage } =
    useMembers(currentPage);

  const totalPages = totalCount ? Math.ceil(totalCount / MEMBERS_PER_PAGE) : 1;
  const startIndex = (currentPage - 1) * MEMBERS_PER_PAGE;

  if (error) {
    return (
      <section className="flex flex-col gap-6">
        <div className="p-4 bg-red-950/30 border border-dashed border-red-900 text-red-500 font-mono text-xs uppercase tracking-wider">
          // ERR: FAILED_TO_LOAD_LEADERBOARD
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <h2 className="text-xl font-bold tracking-tighter text-foreground uppercase">
          Collective Leaderboard
        </h2>
        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
          <Trophy className="w-3.5 h-3.5 text-accent" />
          <span>[ MERITOCRACY_RANKING ]</span>
        </div>
      </div>

      <div className="bg-secondary/10 border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed w-16 text-center">
                  Rnk
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed">
                  Engineer
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed">
                  Tier
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed text-right">
                  Score
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed hidden md:table-cell">
                  Impact
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed hidden lg:table-cell">
                  Lines
                </th>
                <th className="p-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest hidden lg:table-cell">
                  Badges
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading && members.length === 0
                ? // Loading skeletons
                  Array.from({ length: MEMBERS_PER_PAGE }).map((_, i) => (
                    <tr key={i} className="bg-secondary/5 animate-pulse">
                      <td className="p-4 border-r border-dashed border-border-dashed">
                        <div className="h-6 w-6 bg-secondary mx-auto" />
                      </td>
                      <td className="p-4 border-r border-dashed border-border-dashed">
                        <div className="h-4 w-32 bg-secondary" />
                      </td>
                      <td className="p-4 border-r border-dashed border-border-dashed">
                        <div className="h-4 w-16 bg-secondary" />
                      </td>
                      <td className="p-4 border-r border-dashed border-border-dashed">
                        <div className="h-4 w-20 bg-secondary ml-auto" />
                      </td>
                      <td className="p-4 border-r border-dashed border-border-dashed hidden md:table-cell">
                        <div className="h-4 w-24 bg-secondary" />
                      </td>
                      <td className="p-4 border-r border-dashed border-border-dashed hidden lg:table-cell">
                        <div className="h-4 w-40 bg-secondary" />
                      </td>
                      <td className="p-4 hidden lg:table-cell">
                        <div className="h-4 w-40 bg-secondary" />
                      </td>
                    </tr>
                  ))
                : members.map((member, index) => {
                    const tierStyle =
                      TIER_COLORS[member.tier as keyof typeof TIER_COLORS];
                    const globalRank = startIndex + index + 1;
                    return (
                      <tr
                        key={member.id}
                        className="group hover:bg-secondary/20 transition-colors"
                      >
                        <td className="p-4 font-mono text-muted-foreground user-select-none border-r border-dashed border-border-dashed text-center">
                          <div className="text-xs">
                            {globalRank.toString().padStart(2, "0")}
                          </div>
                        </td>
                        <td className="p-4 border-r border-dashed border-border-dashed">
                          <div className="flex items-center gap-3">
                            <img
                              src={member.avatar}
                              alt={member.name}
                              className="w-10 h-10 border border-border grayscale group-hover:grayscale-0 transition-all select-none"
                              referrerPolicy="no-referrer"
                              draggable={false}
                            />
                            <div>
                              <p className="font-bold text-foreground text-sm lowercase tracking-tight">
                                {member.name}
                              </p>
                              <div className="flex items-center gap-1 text-[10px] font-mono text-muted-foreground mt-1 uppercase tracking-wider">
                                <Github className="w-3 h-3" />
                                <span>{member.github}</span>
                                <span className="mx-1 text-border-dashed">
                                  /
                                </span>
                                <span>
                                  {member.contributions.toLocaleString()}{" "}
                                  CONTRIB
                                </span>
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 border-r border-dashed border-border-dashed">
                          <span
                            className={`px-2 py-1 text-[10px] font-mono border uppercase tracking-wider ${tierStyle.bg} ${tierStyle.color} ${tierStyle.border}`}
                          >
                            {member.tier}
                          </span>
                        </td>
                        <td className="p-4 text-right user-select-none border-r border-dashed border-border-dashed">
                          <div className="font-mono font-bold text-accent text-sm">
                            <Counter value={member.score} />
                          </div>
                        </td>
                        <td className="p-4 hidden md:table-cell user-select-none border-r border-dashed border-border-dashed">
                          <div className="flex items-center gap-3">
                            <div className="flex-grow h-1 bg-secondary overflow-hidden w-24">
                              <div
                                className="h-full"
                                style={{
                                  width: `${member.impact}%`,
                                  backgroundColor:
                                    TIER_BAR_COLORS[
                                      member.tier as keyof typeof TIER_BAR_COLORS
                                    ],
                                }}
                              />
                            </div>
                            <span className="text-[10px] font-mono text-muted-foreground w-8">
                              {member.impact}%
                            </span>
                          </div>
                        </td>
                        <td className="p-4 hidden lg:table-cell user-select-none border-r border-dashed border-border-dashed">
                          <div className="flex items-center gap-3 text-[10px] font-mono">
                            <span className="text-accent">
                              +{member.additions.toLocaleString()}
                            </span>
                            <span className="text-red-400">
                              -{member.deletions.toLocaleString()}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 hidden lg:table-cell user-select-none">
                          <div className="flex flex-wrap gap-2">
                            {member.badges.map((badge) => (
                              <span
                                key={badge}
                                className="flex items-center gap-1 px-1.5 py-0.5 text-[9px] uppercase tracking-widest font-mono border border-border bg-background text-muted-foreground"
                                title={badge}
                              >
                                {badge === "Architect" && (
                                  <Shield className="w-2.5 h-2.5 text-purple-400" />
                                )}
                                {badge === "Visionary" && (
                                  <Star className="w-2.5 h-2.5 text-amber-400" />
                                )}
                                {badge === "Reviewer" && (
                                  <Award className="w-2.5 h-2.5 text-blue-400" />
                                )}
                                {badge === "Optimizer" && (
                                  <Zap className="w-2.5 h-2.5 text-accent" />
                                )}
                                {badge}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-border bg-secondary/30">
            <div className="text-[10px] uppercase font-mono text-muted-foreground tracking-widest">
              // IDX: {startIndex.toString().padStart(2, "0")} -{" "}
              {(Math.min(startIndex + MEMBERS_PER_PAGE, totalCount) - 1)
                .toString()
                .padStart(2, "0")}{" "}
              / {totalCount} TOTAL
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 border border-border disabled:opacity-50 disabled:cursor-not-allowed text-muted-foreground hover:bg-foreground hover:text-background transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <div className="px-4 text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                PG_{currentPage.toString().padStart(2, "0")}/
                {totalPages.toString().padStart(2, "0")}
              </div>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages || !hasNextPage}
                className="p-1 border border-border disabled:opacity-50 disabled:cursor-not-allowed text-muted-foreground hover:bg-foreground hover:text-background transition-colors cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
