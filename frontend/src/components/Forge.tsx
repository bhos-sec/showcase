import { Star, GitFork, ExternalLink } from "lucide-react";
import { useState } from "react";
import { useProjects } from "../hooks";
import { INITIAL_PROJECTS_SHOWN, PROJECT_STATUS_COLORS } from "../constants";

export function Forge() {
  const { projects, loading, error } = useProjects();
  const [showAll, setShowAll] = useState(false);
  const displayedProjects = showAll
    ? projects
    : projects.slice(0, INITIAL_PROJECTS_SHOWN);

  if (error) {
    return (
      <section className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
            <span className="text-[var(--color-bhos-mint)]">/</span> Forge
          </h2>
        </div>
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          Failed to load projects. Please try again later.
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
          <span className="text-[var(--color-bhos-mint)]">/</span> Forge
        </h2>
        <button
          onClick={() => setShowAll(!showAll)}
          className="text-sm font-mono text-[var(--color-bhos-mint)] user-select-none"
        >
          {showAll ? "Show Less \u2191" : "View All Projects \u2192"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading && projects.length === 0
          ? // Loading skeletons
            Array.from({ length: INITIAL_PROJECTS_SHOWN }).map((_, i) => (
              <div
                key={i}
                className="bg-slate-800/30 bg-[var(--color-bhos-navy-light)] border border-[var(--color-bhos-border)] rounded-xl p-6 h-64"
              >
                <div className="h-6 bg-slate-700 rounded w-3/4 mb-4" />
                <div className="h-4 bg-slate-700 rounded w-full mb-3" />
                <div className="h-4 bg-slate-700 rounded w-5/6" />
              </div>
            ))
          : displayedProjects.map((project) => (
              <a
                key={project.id}
                href={project.homepage_url || project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative bg-[var(--color-bhos-navy-light)] border border-[var(--color-bhos-border)] hover:border-[var(--color-bhos-mint)] rounded-xl p-6 overflow-hidden transition-colors block"
              >
                <div className="flex flex-col h-full">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-bold text-white user-select-none">
                      {project.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <ExternalLink className="w-4 h-4 text-[var(--color-bhos-mint)] opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                      <span
                        className={`px-2 py-1 text-xs font-mono rounded border ${
                          PROJECT_STATUS_COLORS[
                            project.status as keyof typeof PROJECT_STATUS_COLORS
                          ]
                        }`}
                      >
                        {project.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-400 text-sm mb-6 flex-grow">
                    {project.description}
                  </p>

                  <div className="flex items-center justify-between mt-auto pt-4 border-t border-[var(--color-bhos-border)]">
                    <div className="flex items-center gap-4 text-slate-300 text-sm font-mono user-select-none">
                      <div className="flex items-center gap-1.5">
                        <Star className="w-4 h-4" />
                        <span>{project.stars}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <GitFork className="w-4 h-4" />
                        <span>{project.forks}</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {project.languages.map((lang) => (
                        <span
                          key={lang}
                          className="w-2 h-2 rounded-full bg-[var(--color-bhos-mint)] opacity-80"
                          title={lang}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </a>
            ))}
      </div>
    </section>
  );
}
