"use client";

import { motion } from "framer-motion";
import {
  GitPullRequest,
  CircleDot,
  GitCommitHorizontal,
  User,
  FileText,
} from "lucide-react";
import type { GraphNode } from "@/types/api";

const NODE_META: Record<
  string,
  { icon: typeof FileText; noun: string }
> = {
  Decision: { icon: FileText, noun: "decision" },
  PR: { icon: GitPullRequest, noun: "pull request" },
  Issue: { icon: CircleDot, noun: "issue" },
  Commit: { icon: GitCommitHorizontal, noun: "commit" },
  Person: { icon: User, noun: "contributor" },
};

interface GraphPathProps {
  path: GraphNode[];
}

export default function GraphPath({ path }: GraphPathProps) {
  if (path.length === 0) return null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.12 }}
    >
      <div className="mb-8">
        <h2 className="font-serif text-xl sm:text-[23px] font-semibold text-ink tracking-tight">
          Knowledge Graph Traversal
        </h2>
        <p className="mt-1 text-[14px] text-stone">
          Relational entity path traversed across decisions, code artifacts, and people
        </p>
      </div>

      <div className="bg-grid-faint p-6 border border-rule">
        <ol>
          {path.map((node, idx) => {
            const meta = NODE_META[node.label] || NODE_META.Decision;
            const Icon = meta.icon;
            const isLast = idx === path.length - 1;
            const displayKey =
              node.key.length > 36 ? node.key.slice(0, 36) + "…" : node.key;

            return (
              <li key={`${node.label}-${node.key}`} className="flex gap-5">
                <div className="relative flex w-4 flex-col items-center">
                  <span
                    className={`mt-1.5 z-10 h-2.5 w-2.5 rounded-full ${
                      isLast ? "bg-ember" : "bg-graphite"
                    }`}
                  />
                  {!isLast && (
                    <span className="git-spine absolute top-4 bottom-0 w-px bg-rule-strong" />
                  )}
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.08 + idx * 0.06 }}
                  className={`pb-7 ${isLast ? "pb-1" : ""}`}
                >
                  <p className="flex items-center gap-2 text-[11px] uppercase tracking-[0.14em] text-stone">
                    <Icon className="h-3.5 w-3.5" strokeWidth={1.5} />
                    {meta.noun}
                  </p>
                  <p
                    className={`mt-1 font-mono text-[14px] font-medium ${
                      isLast ? "text-ember" : "text-ink"
                    }`}
                  >
                    {displayKey}
                  </p>
                </motion.div>
              </li>
            );
          })}
        </ol>
      </div>
    </motion.section>
  );
}
