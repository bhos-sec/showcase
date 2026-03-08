import { useState, useEffect } from "react";
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
        className={`transition-all duration-700 ease-out transform ${
          isIntersecting
            ? "opacity-100 translate-y-0"
            : "opacity-0 translate-y-12"
        }`}
        style={{ transitionDelay: delay }}
      >
        {children}
      </div>
    </div>
  );
}

export default function App() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans relative selection:bg-accent selection:text-accent-foreground">
      {/* Header Navigation */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 bg-background/80 backdrop-blur-md ${
          scrolled
            ? "border-b border-dashed border-border-dashed"
            : "border-b border-dashed border-transparent"
        }`}
      >
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <img
              src="/bhos-logo.svg"
              alt="BHOS Logo"
              className="h-7 sm:h-9 w-auto object-contain select-none"
              draggable={false}
            />
            <span className="font-mono text-[10px] sm:text-xs text-muted-foreground select-none">
              ×
            </span>
            <Logo className="h-5 sm:h-7 w-auto opacity-90 hover:opacity-100 transition-opacity select-none" />
          </div>
          <nav className="flex items-center gap-0 sm:gap-1">
            <button className="font-mono text-[10px] sm:text-xs tracking-widest uppercase px-2 sm:px-4 py-2 text-muted-foreground hover:text-foreground border border-transparent hover:border-border transition-all duration-100 active:translate-y-px active:translate-x-px">
              Aim
            </button>
            <button className="font-mono text-[10px] sm:text-xs tracking-widest uppercase px-2 sm:px-4 py-2 text-muted-foreground hover:text-foreground border border-transparent hover:border-border transition-all duration-100 active:translate-y-px active:translate-x-px">
              Pillars
            </button>
            <button className="font-mono text-[10px] sm:text-xs tracking-widest uppercase px-2 sm:px-4 py-2 text-muted-foreground hover:text-foreground border border-transparent hover:border-border transition-all duration-100 active:translate-y-px active:translate-x-px hidden sm:block">
              Apply
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-32 flex flex-col gap-16 md:gap-24 overflow-x-hidden">
        {/* Hero Section */}
        <section className="flex flex-col gap-4 md:gap-6 max-w-3xl">
          <RevealSection delay="0.1s">
            <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold tracking-tighter leading-[1.1] text-foreground lowercase break-words">
              the showcase.
            </h1>
          </RevealSection>
          <RevealSection delay="0.2s">
            <p className="text-base sm:text-lg md:text-xl font-mono text-muted-foreground leading-relaxed tracking-tight border-l-2 border-accent pl-4">
              Central engineering hub for the BHOS Software Engineering
              Collective. Build, learn, and collaborate on open-source
              infrastructure.
            </p>
          </RevealSection>
        </section>

        <section
          id="forge"
          className="pt-8 border-t border-dashed border-border-dashed w-full"
        >
          <RevealSection>
            <div className="mono-label mb-6 md:mb-8 text-[10px] md:text-xs break-all">
              § 01 — OVERVIEW // FORGE_PROJECTS
            </div>
          </RevealSection>
          <RevealSection delay="0.1s">
            <Forge />
          </RevealSection>
        </section>

        <section
          id="leaderboard"
          className="pt-8 border-t border-dashed border-border-dashed w-full"
        >
          <RevealSection>
            <div className="mono-label mb-6 md:mb-8 text-[10px] md:text-xs break-all">
              § 02 — RANKING // MERITOCRACY_BOARD
            </div>
          </RevealSection>
          <RevealSection delay="0.1s">
            <Leaderboard />
          </RevealSection>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-dashed border-border-dashed bg-secondary/20 mt-20 md:mt-32">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 md:py-12 flex flex-col md:flex-row items-center justify-between gap-6 md:gap-8">
          <div className="flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left">
            <Logo className="h-5 sm:h-6 w-auto opacity-30 grayscale select-none" />
            <p className="mono-label text-[9px] sm:text-[10px]">
              &copy; {new Date().getFullYear()} BHOS SEC. ALL RIGHTS RESERVED.
            </p>
          </div>
          <div className="flex flex-wrap justify-center items-center gap-4 sm:gap-6 text-[10px] sm:text-xs font-mono text-muted-foreground">
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
