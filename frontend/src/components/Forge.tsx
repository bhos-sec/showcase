import { Star, GitFork, ExternalLink } from 'lucide-react';
import { useState } from 'react';

const INITIAL_PROJECTS_SHOWN = 3;

const MOCK_PROJECTS = [
  {
    id: 1,
    name: 'Lantern',
    description: 'A high-performance, distributed tracing system for microservices.',
    stars: 1240,
    forks: 342,
    languages: ['Rust', 'TypeScript'],
    status: 'Active',
  },
  {
    id: 2,
    name: 'Nexus',
    description: 'Real-time collaborative code editor with CRDTs.',
    stars: 890,
    forks: 156,
    languages: ['Go', 'React'],
    status: 'Beta',
  },
  {
    id: 3,
    name: 'Aegis',
    description: 'Automated vulnerability scanner for CI/CD pipelines.',
    stars: 2105,
    forks: 567,
    languages: ['Python', 'Docker'],
    status: 'Active',
  },
  {
    id: 4,
    name: 'Nova',
    description: 'Serverless edge computing framework built on WebAssembly.',
    stars: 512,
    forks: 89,
    languages: ['Rust', 'Wasm'],
    status: 'Alpha',
  },
  {
    id: 5,
    name: 'Helios',
    description: 'Distributed task queue with priority scheduling.',
    stars: 1024,
    forks: 210,
    languages: ['Go', 'Redis'],
    status: 'Active',
  },
  {
    id: 6,
    name: 'Vanguard',
    description: 'Zero-trust network proxy and identity aware access.',
    stars: 756,
    forks: 134,
    languages: ['C++', 'Lua'],
    status: 'Beta',
  },
];

export function Forge() {
  const [showAll, setShowAll] = useState(false);
  const displayedProjects = showAll ? MOCK_PROJECTS : MOCK_PROJECTS.slice(0, INITIAL_PROJECTS_SHOWN);

  return (
    <section className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-3">
          <span className="text-[var(--color-bhos-mint)]">/</span> Forge
        </h2>
        <button 
          onClick={() => setShowAll(!showAll)}
          className="text-sm font-mono text-[var(--color-bhos-mint)] hover:text-white transition-colors"
        >
          {showAll ? 'Show Less \u2191' : 'View All Projects \u2192'}
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayedProjects.map((project) => (
          <div 
            key={project.id} 
            className="group relative bg-[var(--color-bhos-navy-light)] border border-[var(--color-bhos-border)] rounded-xl p-6 hover:border-[var(--color-bhos-mint)] transition-all duration-300 overflow-hidden"
          >
            {/* Hover glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-bhos-mint-dim)] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            
            <div className="relative z-10 flex flex-col h-full">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-white group-hover:text-[var(--color-bhos-mint)] transition-colors">
                  {project.name}
                </h3>
                <span className="px-2 py-1 text-xs font-mono rounded bg-white/5 text-slate-300 border border-white/10">
                  {project.status}
                </span>
              </div>
              
              <p className="text-slate-400 text-sm mb-6 flex-grow">
                {project.description}
              </p>
              
              <div className="flex items-center justify-between mt-auto pt-4 border-t border-[var(--color-bhos-border)]">
                <div className="flex items-center gap-4 text-slate-300 text-sm font-mono">
                  <div className="flex items-center gap-1.5 hover:text-white transition-colors cursor-pointer">
                    <Star className="w-4 h-4" />
                    <span>{project.stars}</span>
                  </div>
                  <div className="flex items-center gap-1.5 hover:text-white transition-colors cursor-pointer">
                    <GitFork className="w-4 h-4" />
                    <span>{project.forks}</span>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  {project.languages.map(lang => (
                    <span key={lang} className="w-2 h-2 rounded-full bg-[var(--color-bhos-mint)] opacity-80" title={lang} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
