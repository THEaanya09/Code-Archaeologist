"use client";

import { useState, useRef, useEffect } from "react";
import { Loader2 } from "lucide-react";

interface SearchBarProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
  initialQuery?: string;
  suggestions?: string[];
}

export default function SearchBar({
  onSubmit,
  isLoading,
  initialQuery = "",
  suggestions = [],
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (query.trim().length > 3 && !isLoading) {
      onSubmit(query.trim());
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit}>
        <div
          className={`flex items-center gap-4 border bg-surface px-5 py-4 transition-all shadow-xs ${
            isFocused ? "border-charcoal ring-1 ring-charcoal/20" : "border-rule"
          }`}
        >
          <span className="h-5 w-[2px] bg-ember shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                handleSubmit();
              }
            }}
            placeholder="Ask the repository why… (e.g. Why did Flask 1.0 remove flask.ext?)"
            className="flex-1 bg-transparent text-[16px] text-ink placeholder-stone/80 outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={query.trim().length <= 3 || isLoading}
            className="flex items-center gap-2.5 bg-charcoal px-4 py-2 text-[13px] font-medium text-paper transition-opacity disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-90"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" strokeWidth={1.5} />
            ) : (
              <>
                <span>Investigate</span>
                <kbd className="hidden sm:inline font-mono text-[10px] text-paper/70 bg-white/10 px-1 py-0.5 rounded-xs">
                  ⌘↵
                </kbd>
              </>
            )}
          </button>
        </div>
      </form>

      {suggestions.length > 0 && !query && (
        <div className="mt-5 space-y-1.5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-stone mb-2">
            Suggested investigations
          </p>
          {suggestions.slice(0, 4).map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(suggestion);
                onSubmit(suggestion);
              }}
              className="block w-full text-left text-[14px] leading-relaxed text-stone hover:text-ink hover:underline hover:underline-offset-4 decoration-rule py-1"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
