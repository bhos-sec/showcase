import { Logo } from './components/Logo';
import { Forge } from './components/Forge';
import { Leaderboard } from './components/Leaderboard';

export default function App() {
  return (
    <div className="min-h-screen bg-[var(--color-bhos-navy)] text-slate-300 font-sans relative">
      {/* Background Elements */}
      <div className="fixed inset-0 bg-grid pointer-events-none z-0" />
      <div className="fixed top-1/4 left-0 w-full z-0 pointer-events-none">
        <div className="circuit-trace" />
      </div>
      <div className="fixed top-3/4 left-0 w-full z-0 pointer-events-none" style={{ animationDelay: '4s' }}>
        <div className="circuit-trace" />
      </div>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12 md:py-24 flex flex-col gap-24">
        {/* Hero Section */}
        <section className="flex flex-col gap-8 max-w-4xl">
          <Logo className="h-12 md:h-16 w-auto mb-2 self-start" />
          
          <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-600 tracking-tighter leading-[1.1]">
            The Showcase.
          </h1>
          
          <p className="text-xl md:text-2xl font-mono text-slate-400 max-w-3xl leading-relaxed tracking-tight">
            Central engineering hub for the BHOS Software Engineering Collective. 
            Build, learn, and collaborate on open-source infrastructure.
          </p>
        </section>

        <div id="forge">
          <Forge />
        </div>
        
        <div id="leaderboard">
          <Leaderboard />
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[var(--color-bhos-border)] bg-black/40 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <Logo className="h-6 w-auto opacity-50 grayscale" />
            <p className="text-sm text-slate-500 font-mono">
              &copy; {new Date().getFullYear()} BHOS SEC. All rights reserved.
            </p>
          </div>
          <div className="flex items-center gap-6 text-sm font-mono text-slate-500">
            <a href="#" className="hover:text-[var(--color-bhos-mint)] transition-colors">Status</a>
            <a href="#" className="hover:text-[var(--color-bhos-mint)] transition-colors">API</a>
            <a href="#" className="hover:text-[var(--color-bhos-mint)] transition-colors">GitHub</a>
            <a href="#" className="hover:text-[var(--color-bhos-mint)] transition-colors">Discord</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
