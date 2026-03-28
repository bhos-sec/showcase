import { Trophy, Github, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { useMembers } from "../hooks";
import { MEMBERS_PER_PAGE, TIER_COLORS } from "../constants";
import { BadgeList } from "./Badge";
import type { Member } from "../types/api";

const TIER_BAR_COLORS = {
  Founder: "rgb(192, 132, 250)", // purple-400
  Lead: "rgb(251, 191, 36)", // amber-400
  Mentor: "rgb(96, 165, 250)", // blue-400
  Member: "rgb(0, 255, 166)", // mint
  Learner: "rgb(148, 163, 184)", // slate-400
} as const;

type LeaderboardMode = "total" | "weekly" | "monthly";

function Counter({ value }: { value: number | string }) {
  const numValue = typeof value === "string" ? parseFloat(value) : value;
  return <span>{numValue.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>;
}

function getScoreByMode(member: Member, mode: LeaderboardMode): number {
  if (mode === "weekly") {
    return parseFloat(member.weekly_score || "0");
  }
  if (mode === "monthly") {
    return parseFloat(member.monthly_score || "0");
  }
  return parseFloat(member.score || "0");
}

function getContributionsByMode(member: Member, mode: LeaderboardMode): number {
  if (mode === "weekly") {
    return member.weekly_contribution_count ?? 0;
  }
  if (mode === "monthly") {
    return member.monthly_contribution_count ?? 0;
  }
  return member.contributions ?? 0;
}

export function Leaderboard() {
  const [currentPage, setCurrentPage] = useState(1);
  const [mode, setMode] = useState<LeaderboardMode>("total");
  const { members, loading, error, totalCount, hasNextPage } = useMembers(
    currentPage,
    MEMBERS_PER_PAGE
  );

  const sortedMembers = [...members].sort((a, b) => {
    const scoreDiff = getScoreByMode(b, mode) - getScoreByMode(a, mode);
    if (scoreDiff !== 0) return scoreDiff;

    const contributionDiff =
      getContributionsByMode(b, mode) - getContributionsByMode(a, mode);
    if (contributionDiff !== 0) return contributionDiff;

    return a.name.localeCompare(b.name);
  });

  const totalPages = totalCount ? Math.ceil(totalCount / MEMBERS_PER_PAGE) : 1;
  const startIndex = (currentPage - 1) * MEMBERS_PER_PAGE;

  if (error) {
    return (
      <section className="flex flex-col gap-6">
        <div className="p-4 bg-red-950/30 border border-dashed border-red-900 text-red-500 font-mono text-xs uppercase tracking-wider">
          {/* ERR: FAILED_TO_LOAD_LEADERBOARD */}
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-border pb-4 gap-4 sm:gap-0">
        <h2 className="text-lg md:text-xl font-bold tracking-tighter text-foreground uppercase">
          Collective Leaderboard
        </h2>
        <div className="flex items-center gap-2 md:gap-3">
          <div className="flex items-center gap-2 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
            <Trophy className="w-3 md:w-3.5 h-3 md:h-3.5 text-accent" />
            <span>[ MERITOCRACY_RANKING ]</span>
          </div>
          <div className="flex border border-border">
            <button
              onClick={() => setMode("total")}
              className={`px-2 md:px-3 py-1 text-[9px] md:text-[10px] font-mono uppercase tracking-widest transition-colors cursor-pointer ${mode === "total"
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-secondary/40"
                }`}
            >
              Total
            </button>
            <button
              onClick={() => setMode("weekly")}
              className={`px-2 md:px-3 py-1 text-[9px] md:text-[10px] font-mono uppercase tracking-widest transition-colors cursor-pointer border-l border-border ${mode === "weekly"
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-secondary/40"
                }`}
            >
              Weekly
            </button>
            <button
              onClick={() => setMode("monthly")}
              className={`px-2 md:px-3 py-1 text-[9px] md:text-[10px] font-mono uppercase tracking-widest transition-colors cursor-pointer border-l border-border ${mode === "monthly"
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-secondary/40"
                }`}
            >
              Monthly
            </button>
          </div>
        </div>
      </div>

      <div className="bg-secondary/10 border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[600px] md:min-w-full">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed w-12 md:w-16 text-center whitespace-nowrap">
                  Rnk
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed whitespace-nowrap">
                  Engineer
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed whitespace-nowrap">
                  Tier
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed text-right whitespace-nowrap">
                  {mode === "weekly"
                    ? "Score (Week)"
                    : mode === "monthly"
                      ? "Score (Month)"
                      : "Score"}
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed hidden md:table-cell whitespace-nowrap">
                  Impact
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest border-r border-dashed border-border-dashed hidden lg:table-cell whitespace-nowrap">
                  Lines
                </th>
                <th className="p-3 md:p-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest hidden lg:table-cell whitespace-nowrap">
                  Badges
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading && members.length === 0
                ? // Loading skeletons
                Array.from({ length: MEMBERS_PER_PAGE }).map((_, i) => (
                  <tr key={i} className="bg-secondary/5 animate-pulse">
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                      <div className="h-5 w-5 md:h-6 md:w-6 bg-secondary mx-auto" />
                    </td>
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                      <div className="h-3 md:h-4 w-24 md:w-32 bg-secondary" />
                    </td>
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                      <div className="h-3 md:h-4 w-12 md:w-16 bg-secondary" />
                    </td>
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                      <div className="h-3 md:h-4 w-16 md:w-20 bg-secondary ml-auto" />
                    </td>
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed hidden md:table-cell">
                      <div className="h-3 md:h-4 w-20 md:w-24 bg-secondary" />
                    </td>
                    <td className="p-3 md:p-4 border-r border-dashed border-border-dashed hidden lg:table-cell">
                      <div className="h-3 md:h-4 w-32 md:w-40 bg-secondary" />
                    </td>
                    <td className="p-3 md:p-4 hidden lg:table-cell">
                      <div className="h-3 md:h-4 w-32 md:w-40 bg-secondary" />
                    </td>
                  </tr>
                ))
                : sortedMembers.map((member, index) => {
                  const tierStyle =
                    TIER_COLORS[member.tier as keyof typeof TIER_COLORS];
                  const globalRank = startIndex + index + 1;
                  const displayedScore = getScoreByMode(member, mode);
                  const displayedContributions = getContributionsByMode(
                    member,
                    mode
                  );
                  return (
                    <tr
                      key={member.id}
                      className="group hover:bg-secondary/20 transition-colors"
                    >
                      <td className="p-3 md:p-4 font-mono text-muted-foreground user-select-none border-r border-dashed border-border-dashed text-center">
                        <div className="text-[10px] md:text-xs">
                          {globalRank.toString().padStart(2, "0")}
                        </div>
                      </td>
                      <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                        <a
                          href={`https://github.com/${member.github}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 md:gap-3 hover:opacity-80 transition-opacity"
                        >
                          <img
                            src={member.avatar}
                            alt={member.name}
                            className="w-8 h-8 md:w-10 md:h-10 border border-border grayscale group-hover:grayscale-0 transition-all select-none flex-shrink-0"
                            referrerPolicy="no-referrer"
                            draggable={false}
                          />
                          <div>
                            <p className="font-bold text-foreground text-xs md:text-sm tracking-tight break-all">
                              {member.name}
                            </p>
                            <div className="flex flex-wrap items-center gap-1 text-[9px] md:text-[10px] font-mono text-muted-foreground mt-0.5 md:mt-1 uppercase tracking-wider">
                              <Github className="w-2.5 h-2.5 md:w-3 md:h-3" />
                              <span>{member.github}</span>
                              <span className="mx-0.5 md:mx-1 text-border-dashed">
                                /
                              </span>
                              <span>
                                {displayedContributions.toLocaleString()} {" "}
                                CONTRIB
                              </span>
                            </div>
                          </div>
                        </a>
                      </td>
                      <td className="p-3 md:p-4 border-r border-dashed border-border-dashed">
                        <span
                          className={`px-1.5 py-0.5 md:px-2 md:py-1 text-[9px] md:text-[10px] font-mono border uppercase tracking-wider whitespace-nowrap ${tierStyle.bg} ${tierStyle.color} ${tierStyle.border}`}
                        >
                          {member.tier}
                        </span>
                      </td>
                      <td className="p-3 md:p-4 text-right user-select-none border-r border-dashed border-border-dashed">
                        <div className="font-mono font-bold text-accent text-xs md:text-sm">
                          <Counter value={displayedScore} />
                        </div>
                      </td>
                      <td className="p-3 md:p-4 hidden md:table-cell user-select-none border-r border-dashed border-border-dashed">
                        <div className="flex items-center gap-2 md:gap-3">
                          <div className="flex-grow h-0.5 md:h-1 bg-secondary overflow-hidden w-20 md:w-24">
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
                          <span className="text-[9px] md:text-[10px] font-mono text-muted-foreground w-8">
                            {member.impact}%
                          </span>
                        </div>
                      </td>
                      <td className="p-3 md:p-4 hidden lg:table-cell user-select-none border-r border-dashed border-border-dashed">
                        <div className="flex items-center gap-2 md:gap-3 text-[9px] md:text-[10px] font-mono">
                          <span className="text-accent">
                            +{member.additions.toLocaleString()}
                          </span>
                          <span className="text-red-400">
                            -{member.deletions.toLocaleString()}
                          </span>
                        </div>
                      </td>
                      <td className="p-3 md:p-4 hidden lg:table-cell user-select-none">
                        <BadgeList badges={member.badges} />
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between p-3 md:p-4 border-t border-border bg-secondary/30 gap-3 sm:gap-0">
            <div className="text-[9px] md:text-[10px] uppercase font-mono text-muted-foreground tracking-widest text-center sm:text-left">
              {/* IDX: {startIndex.toString().padStart(2, "0")} -{" "} */}
              {(Math.min(startIndex + MEMBERS_PER_PAGE, totalCount) - 1)
                .toString()
                .padStart(2, "0")}{" "}
              / {totalCount} TOTAL
            </div>
            <div className="flex items-center gap-1 w-full sm:w-auto justify-between sm:justify-start">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 px-3 sm:px-1 border border-border disabled:opacity-50 disabled:cursor-not-allowed text-muted-foreground hover:bg-foreground hover:text-background transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <div className="px-4 text-[9px] md:text-[10px] font-mono text-muted-foreground uppercase tracking-widest text-center flex-grow sm:flex-grow-0">
                PG_{currentPage.toString().padStart(2, "0")}/
                {totalPages.toString().padStart(2, "0")}
              </div>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages || !hasNextPage}
                className="p-1 px-3 sm:px-1 border border-border disabled:opacity-50 disabled:cursor-not-allowed text-muted-foreground hover:bg-foreground hover:text-background transition-colors cursor-pointer"
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
