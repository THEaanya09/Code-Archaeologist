"use client";

import { motion } from "framer-motion";
import {
  GitPullRequest,
  CircleDot,
  GitCommitHorizontal,
  FileQuestion,
  ArrowUpRight,
} from "lucide-react";
import type { Decision } from "@/types/api";
import { formatDate, sourceTypeLabel } from "@/lib/utils";

const SOURCE_ICONS: Record<string, typeof GitPullRequest> = {
  github_pr: GitPullRequest,
  github_issue: CircleDot,
  github_commit: GitCommitHorizontal,
  unknown: FileQuestion,
};

interface DecisionCardProps {
  decision: Decision;
  index: number;
  onClick?: () => void;
}

export default function DecisionCard({
  decision,
  index,
  onClick,
}: DecisionCardProps) {
  const Icon = SOURCE_ICONS[decision.source_type] || SOURCE_ICONS.unknown;

  return (
    <motion.article
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.25, delay: Math.min(index * 0.03, 0.3) }}
      onClick={onClick}
      className="group cursor-pointer py-8 sm:py-9 transition-colors"
    >
      <div className="flex items-center gap-2 font-mono text-[12px] text-stone mb-2">
        <Icon className="h-3.5 w-3.5 text-stone" strokeWidth={1.5} />
        <span>
          {sourceTypeLabel(decision.source_type)}
          {decision.source_id != null ? ` #${decision.source_id}` : ""}
        </span>
      </div>

      <h3 className="font-serif text-[17px] sm:text-[18px] leading-snug text-ink font-semibold group-hover:underline group-hover:underline-offset-4 decoration-rule">
        {decision.summary}
      </h3>

      <p className="mt-3 text-[15px] leading-[1.75] text-stone">
        {decision.rationale}
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[12px] text-stone">
        {decision.people?.[0] && (
          <span className="text-ink font-medium">@{decision.people[0]}</span>
        )}
        {decision.dates?.[0] && <span>{formatDate(decision.dates[0])}</span>}
        <span className="capitalize">{decision.confidence}</span>
        {decision.source_url && (
          <a
            href={decision.source_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-ink opacity-0 transition-opacity group-hover:opacity-100 hover:text-ember"
          >
            Source
            <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={1.5} />
          </a>
        )}
      </div>
    </motion.article>
  );
}
