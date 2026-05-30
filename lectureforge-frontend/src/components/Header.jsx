import React from "react";
import { Globe2, Moon, RotateCw, Sun, Zap } from "lucide-react";

export default function Header({ onNewLecture, onThemeToggle, theme }) {
  const isDark = theme === "dark";

  return (
    <header className="sticky top-0 z-30 bg-[var(--app-bg)]/95 px-4 py-5 backdrop-blur sm:px-6">
      <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between rounded-full border border-[var(--app-border)] bg-white/90 px-5 shadow-[0_12px_38px_rgba(20,20,20,0.06)] sm:px-7">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 text-[var(--app-text)]">
            <span className="grid h-9 w-9 rotate-[-12deg] place-items-center rounded-xl bg-[var(--app-purple)] text-white">
              <Zap className="h-5 w-5 fill-current" />
            </span>
            <span className="text-3xl font-black tracking-[-0.04em]">
              LectureForge
            </span>
          </div>

          <button
            type="button"
            onClick={onNewLecture}
            className="hidden items-center gap-2 rounded-full px-3 py-2 text-sm font-semibold text-[var(--app-muted)] transition hover:bg-[var(--app-panel-muted)] lg:inline-flex"
          >
            <RotateCw className="h-4 w-4" />
            New lecture
          </button>
        </div>

        <nav className="hidden items-center gap-8 text-lg font-semibold text-[var(--app-text)] lg:flex">
          <a href="#input" className="transition hover:text-[var(--app-accent)]">
            Tools
          </a>
          <a href="#input" className="transition hover:text-[var(--app-accent)]">
            Mind Maps
          </a>
        </nav>

        <div className="flex items-center gap-3 text-[var(--app-muted)]">
          <button
            type="button"
            onClick={onThemeToggle}
            className="grid h-11 w-11 place-items-center rounded-full transition hover:bg-[var(--app-panel-muted)]"
            aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          <button
            type="button"
            className="hidden h-11 items-center gap-2 rounded-full px-3 text-sm font-semibold text-[var(--app-text)] transition hover:bg-[var(--app-panel-muted)] sm:inline-flex"
          >
            <Globe2 className="h-4 w-4" />
          </button>

          <button
            type="button"
            className="hidden h-11 items-center rounded-xl bg-[var(--app-purple)] px-6 text-base font-bold text-white shadow-sm transition hover:opacity-90 sm:inline-flex"
          >
            Sign in
          </button>

          <button
            type="button"
            className="hidden h-11 items-center rounded-xl bg-[var(--app-accent)] px-6 text-base font-bold text-white shadow-sm transition hover:bg-[var(--app-accent-strong)] sm:inline-flex"
          >
            Start for free
          </button>
        </div>
      </div>
    </header>
  );
}
