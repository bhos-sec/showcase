/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        border: "hsl(var(--border))",
        "border-dashed": "hsl(var(--border-dashed))",
        "grid-line": "hsl(var(--grid-line))",
      },
      borderRadius: {
        lg: "0px",
        md: "0px",
        sm: "0px",
      },
      fontFamily: {
        sans: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'Geist Mono'", "'Courier New'", "monospace"],
      },
      keyframes: {
        slideInLeft: {
          "0%": { transform: "translateX(-10px)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        revealUp: {
          "0%": { transform: "translateY(100%)", opacity: "0" },
          "100%": { transform: "translateY(0%)", opacity: "1" },
        },
        fadeSlideIn: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
      },
      animation: {
        slideInLeft: "slideInLeft 0.4s cubic-bezier(0.16,1,0.3,1) forwards",
        revealUp: "revealUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards",
        fadeSlideIn: "fadeSlideIn 0.5s cubic-bezier(0.16,1,0.3,1) forwards",
        blink: "blink 1s step-end infinite",
      },
    },
  },
  plugins: [],
}
