"use client";

import { useState, useEffect, useCallback } from "react";
import CommandPalette from "@/components/ui/CommandPalette";

interface HeaderProps {
  title: string;
  description?: string;
}

export default function Header({ title, description }: HeaderProps) {
  const [paletteOpen, setPaletteOpen] = useState(false);

  const togglePalette = useCallback(() => {
    setPaletteOpen((prev) => !prev);
  }, []);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        togglePalette();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [togglePalette]);

  return (
    <>
      <header className="sticky top-0 z-30 flex items-end justify-between border-b border-rule bg-paper/92 px-8 sm:px-12 py-7 sm:py-8 backdrop-blur-[3px]">
        <div>
          <h1 className="font-serif text-2xl sm:text-[34px] sm:leading-[1.2] font-bold tracking-tight text-ink">
            {title}
          </h1>
          {description && (
            <p className="mt-2 text-[15px] leading-relaxed text-stone">{description}</p>
          )}
        </div>

        <button
          onClick={togglePalette}
          className="flex items-center gap-2.5 border border-rule bg-surface px-3 py-1.5 text-[13px] text-stone transition-colors hover:border-rule-strong hover:text-ink shadow-xs"
        >
          <span>Search</span>
          <kbd className="font-mono text-[11px] text-stone bg-rule/60 px-1.5 py-0.5 rounded-xs">⌘K</kbd>
        </button>
      </header>

      <CommandPalette isOpen={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  );
}
