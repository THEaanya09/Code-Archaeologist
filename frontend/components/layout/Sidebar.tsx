"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, BookOpen, FolderGit2 } from "lucide-react";
import { cn } from "@/lib/utils";
import GitLogo from "@/components/icons/GitLogo";
import GitHubLogo from "@/components/icons/GitHubLogo";

const NAV_ITEMS = [
  { label: "Repository", href: "/", icon: FolderGit2 },
  { label: "Investigate", href: "/investigate", icon: Search },
  { label: "Decisions", href: "/decisions", icon: BookOpen },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[230px] flex-col border-r border-rule bg-paper">
      <div className="px-6 pt-8 pb-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone">
          Repository
        </p>
        <div className="mt-2.5 flex items-center gap-2">
          <GitLogo className="h-4 w-4 text-ember" />
          <p className="font-mono text-[13px] font-medium text-ink">pallets/flask</p>
        </div>
      </div>

      <div className="mx-6 border-t border-rule" />

      <nav className="flex-1 px-4 py-6 space-y-1.5">
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-3 py-2.5 text-[14px] font-medium transition-colors",
                isActive
                  ? "bg-surface text-ink border-l-2 border-ember font-semibold"
                  : "text-stone hover:text-ink hover:bg-surface/50"
              )}
            >
              <item.icon
                className={cn("h-4 w-4", isActive ? "text-ink" : "text-stone")}
                strokeWidth={1.5}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mx-6 border-t border-rule" />

      <div className="px-4 py-4 space-y-3">
        <a
          href="https://github.com/pallets/flask"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2.5 px-3 py-1.5 text-[13px] text-stone transition-colors hover:text-ink hover:bg-surface/50 rounded-xs"
        >
          <GitHubLogo className="h-4 w-4" />
          <span>GitHub</span>
        </a>

        <div className="border-t border-rule/60 pt-3 px-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-stone/80 mb-2">
            Tracks
          </p>
          <div className="space-y-1.5 font-mono text-[12px]">
            <div className="flex items-center gap-2 text-stone hover:text-ink transition-colors cursor-default">
              <span className="h-1.5 w-1.5 rounded-full bg-ember shrink-0" />
              <span>Neo4j Track</span>
            </div>
            <div className="flex items-center gap-2 text-stone hover:text-ink transition-colors cursor-default">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-note shrink-0" />
              <span>Sarvam Track</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
