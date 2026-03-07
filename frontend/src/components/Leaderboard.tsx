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
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
            <span className="text-[var(--color-bhos-mint)]">/</span> Collective
            Leaderboard
          </h2>
          <div className="flex items-center gap-2 text-sm font-mono text-slate-400">
            <Trophy className="w-4 h-4 text-[var(--color-bhos-mint)]" />
            <span>Meritocracy Ranking</span>
          </div>
        </div>
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          Failed to load leaderboard. Please try again later.
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
          <span className="text-[var(--color-bhos-mint)]">/</span> Collective
          Leaderboard
        </h2>
        <div className="flex items-center gap-2 text-sm font-mono text-slate-400">
          <Trophy className="w-4 h-4 text-[var(--color-bhos-mint)]" />
          <span>Meritocracy Ranking</span>
        </div>
      </div>

      <div className="bg-[var(--color-bhos-navy-light)] border border-[var(--color-bhos-border)] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--color-bhos-border)] bg-black/20">
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Rank
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Engineer
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Tier
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider text-right">
                  Score
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider hidden md:table-cell">
                  Impact
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider hidden lg:table-cell">
                  Lines
                </th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider hidden lg:table-cell">
                  Badges
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-bhos-border)]">
              {loading && members.length === 0
                ? // Loading skeletons
                  Array.from({ length: MEMBERS_PER_PAGE }).map((_, i) => (
                    <tr key={i} className="bg-slate-800/30">
                      <td className="p-4">
                        <div className="h-8 w-8 bg-slate-700 rounded-full" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 w-32 bg-slate-700 rounded" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 w-16 bg-slate-700 rounded" />
                      </td>
                      <td className="p-4">
                        <div className="h-4 w-20 bg-slate-700 rounded ml-auto" />
                      </td>
                      <td className="p-4 hidden md:table-cell">
                        <div className="h-4 w-24 bg-slate-700 rounded" />
                      </td>
                      <td className="p-4 hidden lg:table-cell">
                        <div className="h-4 w-40 bg-slate-700 rounded" />
                      </td>
                      <td className="p-4 hidden lg:table-cell">
                        <div className="h-4 w-40 bg-slate-700 rounded" />
                      </td>
                    </tr>
                  ))
                : members.map((member, index) => {
                    const tierStyle =
                      TIER_COLORS[member.tier as keyof typeof TIER_COLORS];
                    const globalRank = startIndex + index + 1;
                    return (
                      <tr key={member.id} className="group">
                        <td className="p-4 font-mono text-slate-400 user-select-none">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-black/30 border border-[var(--color-bhos-border)]">
                            {globalRank}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <img
                              src={member.avatar}
                              alt={member.name}
                              className="w-10 h-10 rounded-full border border-[var(--color-bhos-border)]"
                              referrerPolicy="no-referrer"
                            />
                            <div>
                              <p className="font-bold text-white">
                                {member.name}
                              </p>
                              <div className="flex items-center gap-1 text-xs font-mono text-slate-400 mt-1">
                                <Github className="w-3 h-3" />
                                <span>{member.github}</span>
                                <span className="mx-1">&bull;</span>
                                <span>
                                  {member.contributions.toLocaleString()}{" "}
                                  contributions
                                </span>
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span
                            className={`px-2.5 py-1 text-xs font-mono rounded border ${tierStyle.bg} ${tierStyle.color} ${tierStyle.border}`}
                          >
                            {member.tier}
                          </span>
                        </td>
                        <td className="p-4 text-right user-select-none">
                          <div className="font-mono font-bold text-white text-lg">
                            <Counter value={member.score} />
                          </div>
                        </td>
                        <td className="p-4 hidden md:table-cell user-select-none">
                          <div className="flex items-center gap-3">
                            <div className="flex-grow h-1.5 bg-black/50 rounded-full overflow-hidden w-24">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${member.impact}%`,
                                  backgroundColor:
                                    TIER_BAR_COLORS[
                                      member.tier as keyof typeof TIER_BAR_COLORS
                                    ],
                                }}
                              />
                            </div>
                            <span className="text-xs font-mono text-slate-400 w-8">
                              {member.impact}%
                            </span>
                          </div>
                        </td>
                        <td className="p-4 hidden lg:table-cell user-select-none">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono text-green-400">
                              +{member.additions.toLocaleString()}
                            </span>
                            <span className="text-xs font-mono text-orange-400">
                              -{member.deletions.toLocaleString()}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 hidden lg:table-cell user-select-none">
                          <div className="flex gap-2">
                            {member.badges.map((badge) => (
                              <span
                                key={badge}
                                className="flex items-center gap-1 px-2 py-1 text-[10px] uppercase tracking-wider font-mono rounded bg-black/30 text-slate-300 border border-[var(--color-bhos-border)]"
                                title={badge}
                              >
                                {badge === "Architect" && (
                                  <Shield className="w-3 h-3 text-purple-400" />
                                )}
                                {badge === "Visionary" && (
                                  <Star className="w-3 h-3 text-amber-400" />
                                )}
                                {badge === "Reviewer" && (
                                  <Award className="w-3 h-3 text-blue-400" />
                                )}
                                {badge === "Optimizer" && (
                                  <Zap className="w-3 h-3 text-[var(--color-bhos-mint)]" />
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
          <div className="flex items-center justify-between p-4 border-t border-[var(--color-bhos-border)] bg-black/20">
            <div className="text-xs font-mono text-slate-400">
              Showing {startIndex + 1} to{" "}
              {Math.min(startIndex + MEMBERS_PER_PAGE, totalCount)} of{" "}
              {totalCount} engineers
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 user-select-none"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <div className="text-xs font-mono text-slate-400 user-select-none">
                Page {currentPage} of {totalPages}
              </div>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages || !hasNextPage}
                className="p-1 rounded disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 user-select-none"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
