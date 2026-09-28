"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  GitPullRequest,
  CircleDot,
  GitCommitHorizontal,
  FileQuestion,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
} from "lucide-react";
import type { Evidence } from "@/types/api";
import { formatDate, sourceTypeLabel } from "@/lib/utils";

const SOURCE_ICONS: Record<string, typeof GitPullRequest> = {
  github_pr: GitPullRequest,
  github_issue: CircleDot,
  github_commit: GitCommitHorizontal,
  unknown: FileQuestion,
};

interface EvidenceCardProps {
  evidence: Evidence;
  index: number;
}

export default function EvidenceCard({ evidence, index }: EvidenceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const Icon = SOURCE_ICONS[evidence.source_type] || SOURCE_ICONS.unknown;
  const heading = evidence.source_id
    ? `${sourceTypeLabel(evidence.source_type)} #${evidence.source_id}`
    : sourceTypeLabel(evidence.source_type);

  return (
    <motion.article
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.25, delay: index * 0.05 }}
      className="py-8 sm:py-9 first:pt-4"
    >
      <div className="flex items-center gap-2 font-mono text-[12px] text-stone">
        <Icon className="h-3.5 w-3.5 text-stone" strokeWidth={1.5} />
        <span>{heading}</span>
      </div>

      <h3 className="mt-2.5 text-[17px] leading-snug text-ink font-medium">
        {evidence.summary}
      </h3>

      <p className="mt-3 text-[15px] leading-[1.75] text-stone">
        {evidence.rationale}
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[12px] text-stone">
        {evidence.people.map((p) => (
          <span key={p} className="text-ink font-medium">
            @{p}
          </span>
        ))}
        {evidence.dates[0] && <span>{formatDate(evidence.dates[0])}</span>}
        <span className="text-stone">relevance {evidence.score.toFixed(3)}</span>
        <span className="capitalize">{evidence.confidence}</span>
        {evidence.source_url && (
          <a
            href={evidence.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-ink hover:text-ember transition-colors"
          >
            Source
            <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={1.5} />
          </a>
        )}
      </div>

      {evidence.evidence_snippet && (
        <div className="mt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center gap-1.5 text-[13px] text-stone hover:text-ink transition-colors"
          >
            {isExpanded ? "Hide raw excerpt" : "View raw excerpt"}
            {isExpanded ? (
              <ChevronUp className="h-3.5 w-3.5" strokeWidth={1.5} />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" strokeWidth={1.5} />
            )}
          </button>
          {isExpanded && (
            <div className="mt-3 p-4 bg-surface/80 border-l-2 border-ember border-y border-r border-rule">
              <p className="text-[14px] leading-[1.7] text-graphite italic">
                “{evidence.evidence_snippet}”
              </p>
            </div>
          )}
        </div>
      )}
    </motion.article>
  );
}
