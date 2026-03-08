import { Logo } from "./components/Logo";
import { Forge } from "./components/Forge";
import { Leaderboard } from "./components/Leaderboard";
import { useIntersectionObserver } from "./hooks/useIntersectionObserver";

function RevealSection({
  children,
  className = "",
  delay = "0s",
}: {
  children: React.ReactNode;
  className?: string;
  delay?: string;
}) {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.1 });

  return (
    <div ref={ref} className={`overflow-hidden ${className}`}>
      <div
        className="opacity-0 translate-y-[100%]"
        style={{
          animation: isIntersecting
            ? `revealUp 0.6s cubic-bezier(0.16,1,0.3,1) ${delay} forwards`
            : "none",
        }}
      >
        {children}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground font-sans relative selection:bg-accent selection:text-accent-foreground">
      {/* Main Content */}
      <main className="relative z-10 max-w-6xl mx-auto px-6 py-12 md:py-24 flex flex-col gap-32">
        {/* Navigation / Header */}
        <header className="flex justify-between items-start border-b border-dashed border-border-dashed pb-6">
          <RevealSection>
            <Logo className="h-10 w-auto mb-2 opacity-90 hover:opacity-100 transition-opacity" />
            <div className="mono-label mt-2 text-[10px] text-muted-foreground tracking-widest">
              // SYS.INIT: CORE_HUB
            </div>
          </RevealSection>
          <RevealSection delay="0.1s">
            <div className="flex gap-6">
              <span className="mono-label cursor-pointer hover:text-accent transition-colors">
                [01] STATUS
              </span>
              <span className="mono-label cursor-pointer hover:text-accent transition-colors">
                [02] DOCS
              </span>
            </div>
          </RevealSection>
        </header>

        {/* Hero Section */}
        <section className="flex flex-col gap-6 max-w-3xl">
          <RevealSection delay="0.2s">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-[1.1] text-foreground lowercase">
              the showcase.
            </h1>
          </RevealSection>
          <RevealSection delay="0.3s">
            <p className="text-lg md:text-xl font-mono text-muted-foreground leading-relaxed tracking-tight border-l-2 border-accent pl-4">
              Central engineering hub for the BHOS Software Engineering
              Collective. Build, learn, and collaborate on open-source
              infrastructure.
            </p>
          </RevealSection>
          <RevealSection delay="0.4s">
            <div className="flex gap-4 mt-6">
              <button className="btn-mechanical group">
                Initialize{" "}
                <span className="inline-block w-2 bg-accent h-4 ml-2 align-middle opacity-0 group-hover:opacity-100 animate-blink"></span>
              </button>
              <button className="btn-mechanical bg-secondary/30 border-dashed border-border-dashed hover:border-accent">
                Documentation
              </button>
            </div>
          </RevealSection>
        </section>

        <section
          id="forge"
          className="pt-8 border-t border-dashed border-border-dashed"
        >
          <RevealSection>
            <div className="mono-label mb-8">
              § 01 — OVERVIEW // FORGE_PROJECTS
            </div>
          </RevealSection>
          <RevealSection delay="0.1s">
            <Forge />
          </RevealSection>
        </section>

        <section
          id="leaderboard"
          className="pt-8 border-t border-dashed border-border-dashed"
        >
          <RevealSection>
            <div className="mono-label mb-8">
              § 02 — RANKING // MERITOCRACY_BOARD
            </div>
          </RevealSection>
          <RevealSection delay="0.1s">
            <Leaderboard />
          </RevealSection>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-dashed border-border-dashed bg-secondary/20 mt-32">
        <div className="max-w-6xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <Logo className="h-6 w-auto opacity-30 grayscale" />
            <p className="mono-label text-[10px]">
              &copy; {new Date().getFullYear()} BHOS SEC. ALL RIGHTS RESERVED.
            </p>
          </div>
          <div className="flex items-center gap-6 text-xs font-mono text-muted-foreground">
            <a
              href="#"
              className="hover:text-accent transition-colors uppercase"
            >
              // STATUS
            </a>
            <a
              href="#"
              className="hover:text-accent transition-colors uppercase"
            >
              // API
            </a>
            <a
              href="#"
              className="hover:text-accent transition-colors uppercase"
            >
              // GITHUB
            </a>
            <a
              href="#"
              className="hover:text-accent transition-colors uppercase"
            >
              // DISCORD
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
