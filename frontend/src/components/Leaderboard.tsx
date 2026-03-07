import { Trophy, Github, Star, Shield, Award, Zap, ChevronLeft, ChevronRight } from 'lucide-react';
import { useEffect, useState } from 'react';

const USERS_PER_PAGE = 25;

const TIERS = {
  Founder: { color: 'text-purple-400', bg: 'bg-purple-400/10', border: 'border-purple-400/30' },
  Lead: { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/30' },
  Mentor: { color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/30' },
  Member: { color: 'text-[var(--color-bhos-mint)]', bg: 'bg-[var(--color-bhos-mint-dim)]', border: 'border-[var(--color-bhos-mint)]/30' },
  Learner: { color: 'text-slate-400', bg: 'bg-slate-400/10', border: 'border-slate-400/30' },
};

const generateMockUsers = (count: number) => {
  const baseUsers = [
    { name: 'Eleanor Shellstrop', tier: 'Founder', github: 'eleanor', badges: ['Architect', 'Visionary'] },
    { name: 'Chidi Anagonye', tier: 'Lead', github: 'chidi', badges: ['Reviewer', 'Optimizer'] },
    { name: 'Tahani Al-Jamil', tier: 'Mentor', github: 'tahani', badges: ['Guide', 'Speaker'] },
    { name: 'Jason Mendoza', tier: 'Member', github: 'jason', badges: ['Hacker', 'Fast Learner'] },
    { name: 'Michael', tier: 'Learner', github: 'michael', badges: ['Newcomer'] },
  ];

  return Array.from({ length: count }, (_, i) => {
    const base = baseUsers[i % baseUsers.length];
    const score = Math.max(100, 15000 - i * 400 + Math.floor(Math.random() * 200));
    return {
      id: i + 1,
      name: i < 5 ? base.name : `${base.name.split(' ')[0]} Clone ${i + 1}`,
      tier: base.tier,
      score: score,
      github: i < 5 ? base.github : `${base.github}${i+1}`,
      contributions: Math.floor(score / 4.5),
      impact: Math.max(10, 98 - Math.floor(i * 2.5)),
      badges: base.badges,
      avatar: `https://i.pravatar.cc/150?u=${base.github}${i}`,
    };
  }).sort((a, b) => b.score - a.score);
};

// Generate 32 mock users to demonstrate pagination (more than USERS_PER_PAGE)
const MOCK_LEADERBOARD = generateMockUsers(32);

function AnimatedCounter({ value }: { value: number }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    const duration = 1500;
    const increment = end / (duration / 16); // 60fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value]);

  return <span>{count.toLocaleString()}</span>;
}

export function Leaderboard() {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(MOCK_LEADERBOARD.length / USERS_PER_PAGE);
  
  const startIndex = (currentPage - 1) * USERS_PER_PAGE;
  const displayedUsers = MOCK_LEADERBOARD.slice(startIndex, startIndex + USERS_PER_PAGE);

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
          <span className="text-[var(--color-bhos-mint)]">/</span> Collective Leaderboard
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
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">Rank</th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">Engineer</th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider">Tier</th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider text-right">Score</th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider hidden md:table-cell">Impact</th>
                <th className="p-4 text-xs font-mono text-slate-400 uppercase tracking-wider hidden lg:table-cell">Badges</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-bhos-border)]">
              {displayedUsers.map((user, index) => {
                const tierStyle = TIERS[user.tier as keyof typeof TIERS];
                const globalRank = startIndex + index + 1;
                return (
                  <tr 
                    key={user.id} 
                    className="hover:bg-white/5 transition-colors group"
                  >
                    <td className="p-4 font-mono text-slate-400">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-black/30 border border-[var(--color-bhos-border)] group-hover:border-[var(--color-bhos-mint)] transition-colors">
                        {globalRank}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <img 
                          src={user.avatar} 
                          alt={user.name} 
                          className="w-10 h-10 rounded-full border border-[var(--color-bhos-border)]"
                          referrerPolicy="no-referrer"
                        />
                        <div>
                          <p className="font-bold text-white group-hover:text-[var(--color-bhos-mint)] transition-colors">
                            {user.name}
                          </p>
                          <div className="flex items-center gap-1 text-xs font-mono text-slate-400 mt-1">
                            <Github className="w-3 h-3" />
                            <span>{user.github}</span>
                            <span className="mx-1">&bull;</span>
                            <span>{user.contributions.toLocaleString()} commits</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 text-xs font-mono rounded border ${tierStyle.bg} ${tierStyle.color} ${tierStyle.border}`}>
                        {user.tier}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="font-mono font-bold text-white text-lg">
                        <AnimatedCounter value={user.score} />
                      </div>
                    </td>
                    <td className="p-4 hidden md:table-cell">
                      <div className="flex items-center gap-3">
                        <div className="flex-grow h-1.5 bg-black/50 rounded-full overflow-hidden w-24">
                          <div 
                            className={`h-full rounded-full ${tierStyle.bg.replace('/10', '')}`}
                            style={{ width: `${user.impact}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-slate-400 w-8">{user.impact}%</span>
                      </div>
                    </td>
                    <td className="p-4 hidden lg:table-cell">
                      <div className="flex gap-2">
                        {user.badges.map(badge => (
                          <span 
                            key={badge} 
                            className="flex items-center gap-1 px-2 py-1 text-[10px] uppercase tracking-wider font-mono rounded bg-black/30 text-slate-300 border border-[var(--color-bhos-border)]"
                            title={badge}
                          >
                            {badge === 'Architect' && <Shield className="w-3 h-3 text-purple-400" />}
                            {badge === 'Visionary' && <Star className="w-3 h-3 text-amber-400" />}
                            {badge === 'Reviewer' && <Award className="w-3 h-3 text-blue-400" />}
                            {badge === 'Optimizer' && <Zap className="w-3 h-3 text-[var(--color-bhos-mint)]" />}
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
              Showing {startIndex + 1} to {Math.min(startIndex + USERS_PER_PAGE, MOCK_LEADERBOARD.length)} of {MOCK_LEADERBOARD.length} engineers
            </div>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <div className="text-xs font-mono text-slate-400">
                Page {currentPage} of {totalPages}
              </div>
              <button 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1 rounded hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 hover:text-white transition-colors"
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
