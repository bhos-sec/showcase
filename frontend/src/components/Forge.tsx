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
        <div className="p-4 bg-red-950/30 border border-dashed border-red-900 text-red-500 font-mono text-xs uppercase tracking-wider">
          // ERR: FAILED_TO_LOAD_PROJECTS
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <h2 className="text-xl font-bold tracking-tighter text-foreground uppercase">
          Forge Projects
        </h2>
        <button
          onClick={() => setShowAll(!showAll)}
          className="btn-mechanical text-xs px-4 py-2"
        >
          {showAll ? "[ SHOW_LESS ]" : "[ VIEW_ALL_PROJECTS ]"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading && projects.length === 0
          ? // Loading skeletons
            Array.from({ length: INITIAL_PROJECTS_SHOWN }).map((_, i) => (
              <div
                key={i}
                className="bg-secondary/10 border-dashed border-border-dashed p-6 h-64"
              >
                <div className="h-6 bg-secondary rounded-none w-3/4 mb-4 animate-pulse" />
                <div className="h-4 bg-secondary rounded-none w-full mb-3 animate-pulse" />
                <div className="h-4 bg-secondary rounded-none w-5/6 animate-pulse" />
              </div>
            ))
          : displayedProjects.map((project) => (
              <a
                key={project.id}
                href={project.homepage_url || project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative bg-secondary/10 border border-border hover:border-accent p-6 overflow-hidden transition-colors block"
              >
                <div className="flex flex-col h-full">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-bold text-foreground user-select-none lowercase tracking-tight">
                      {project.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <ExternalLink className="w-4 h-4 text-accent opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                      <span
                        className={`px-2 py-1 text-[10px] uppercase font-mono border-dashed border ${
                          PROJECT_STATUS_COLORS[
                            project.status as keyof typeof PROJECT_STATUS_COLORS
                          ]
                        }`}
                      >
                        {project.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-muted-foreground text-sm mb-6 flex-grow leading-relaxed font-mono">
                    {project.description}
                  </p>

                  <div className="flex items-center justify-between mt-auto pt-4 border-t border-dashed border-border-dashed">
                    <div className="flex items-center gap-4 text-muted-foreground text-xs font-mono user-select-none">
                      <div className="flex items-center gap-1.5 hover:text-accent transition-colors">
                        <Star className="w-3.5 h-3.5" />
                        <span>{project.stars}</span>
                      </div>
                      <div className="flex items-center gap-1.5 hover:text-accent transition-colors">
                        <GitFork className="w-3.5 h-3.5" />
                        <span>{project.forks}</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {project.languages.map((lang) => (
                        <span
                          key={lang}
                          className="w-1.5 h-1.5 rounded-none bg-accent opacity-80 group-hover:animate-pulse"
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
