"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search, ArrowRight, MessageSquare, BookOpen, FolderGit2 } from "lucide-react";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const NAVIGATION_ITEMS = [
  { label: "Investigate", description: "Ask a why-code question", href: "/investigate", icon: Search },
  { label: "Decisions", description: "Browse the decision archive", href: "/decisions", icon: BookOpen },
  { label: "Repository", description: "Repository briefing", href: "/", icon: FolderGit2 },
];

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const filteredItems = NAVIGATION_ITEMS.filter(
    (item) =>
      item.label.toLowerCase().includes(query.toLowerCase()) ||
      item.description.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = useCallback(
    (href: string) => {
      onClose();
      setQuery("");
      router.push(href);
    },
    [onClose, router]
  );

  const handleInvestigate = useCallback(() => {
    if (query.trim().length > 3) {
      onClose();
      router.push(`/investigate?q=${encodeURIComponent(query.trim())}`);
      setQuery("");
    }
  }, [query, onClose, router]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
    }
  }, [isOpen]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 z-50 bg-ink/20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed left-1/2 top-[18%] z-50 w-full max-w-lg -translate-x-1/2"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.12 }}
          >
            <div className="overflow-hidden border border-rule bg-surface shadow-[0_12px_40px_rgba(28,28,26,0.08)]">
              <div className="flex items-center gap-3 border-b border-rule px-4 py-3">
                <Search className="h-4 w-4 text-stone" strokeWidth={1.5} />
                <input
                  ref={inputRef}
                  type="text"
                  className="flex-1 bg-transparent text-sm text-ink placeholder-stone outline-none"
                  placeholder="Search or ask a question…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleInvestigate();
                  }}
                />
                <kbd className="hidden font-mono text-[10px] text-stone sm:inline">
                  ESC
                </kbd>
              </div>

              <div className="max-h-80 overflow-y-auto py-1">
                {query.trim().length > 3 && (
                  <button
                    onClick={handleInvestigate}
                    className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-paper"
                  >
                    <MessageSquare className="h-4 w-4 text-ember" strokeWidth={1.5} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-ink truncate">
                        Investigate: “{query}”
                      </p>
                      <p className="text-[12px] text-stone">Ask the repository</p>
                    </div>
                    <ArrowRight className="h-3.5 w-3.5 text-stone" strokeWidth={1.5} />
                  </button>
                )}

                {filteredItems.length > 0 && (
                  <>
                    <p className="px-4 pt-2 pb-1 text-[10px] font-medium uppercase tracking-[0.14em] text-stone">
                      Go to
                    </p>
                    {filteredItems.map((item) => (
                      <button
                        key={item.href}
                        onClick={() => handleSelect(item.href)}
                        className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-paper"
                      >
                        <item.icon className="h-4 w-4 text-stone" strokeWidth={1.5} />
                        <div className="flex-1">
                          <p className="text-sm text-ink">{item.label}</p>
                          <p className="text-[12px] text-stone">{item.description}</p>
                        </div>
                        <ArrowRight className="h-3.5 w-3.5 text-stone" strokeWidth={1.5} />
                      </button>
                    ))}
                  </>
                )}
              </div>

              <div className="flex items-center justify-between border-t border-rule px-4 py-2">
                <span className="font-mono text-[10px] text-stone">⌘K</span>
                <span className="font-mono text-[10px] text-stone">↵ select</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
