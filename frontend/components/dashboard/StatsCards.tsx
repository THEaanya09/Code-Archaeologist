"use client";

import { motion } from "framer-motion";
import type { StatsResponse } from "@/types/api";

interface StatsCardsProps {
  stats: StatsResponse;
}

function sourceLabel(type: string) {
  return type
    .replace("github_", "")
    .replace("_", " ")
    .replace(/^\w/, (c) => c.toUpperCase());
}

export default function StatsCards({ stats }: StatsCardsProps) {
  const totalSources = Object.values(stats.source_type_distribution).reduce(
    (a, b) => a + b,
    0
  );

  return (
    <div className="space-y-16">
      <div>
        <div className="mb-6">
          <h2 className="font-serif text-xl sm:text-[23px] font-semibold text-ink tracking-tight">
            Repository Signals
          </h2>
          <p className="mt-1 text-[14px] text-stone">
            Structural metrics and indexed discussion volume
          </p>
        </div>

        <dl className="grid grid-cols-1 sm:grid-cols-3 gap-x-10 gap-y-4 text-[14px]">
          <div className="flex items-baseline justify-between gap-4 border-b border-rule pb-3">
            <dt className="text-stone">Decisions discovered</dt>
            <dd className="font-mono text-[15px] font-medium text-ink">{stats.decision_count}</dd>
          </div>
          <div className="flex items-baseline justify-between gap-4 border-b border-rule pb-3">
            <dt className="text-stone">Catalogued questions</dt>
            <dd className="font-mono text-[15px] font-medium text-ink">{stats.golden_question_count}</dd>
          </div>
          <div className="flex items-baseline justify-between gap-4 border-b border-rule pb-3">
            <dt className="text-stone">Contributors</dt>
            <dd className="font-mono text-[15px] font-medium text-ink">{stats.contributor_count}</dd>
          </div>
        </dl>
      </div>

      {totalSources > 0 && (
        <div>
          <h3 className="font-serif text-[17px] font-semibold text-ink tracking-tight mb-3">
            Source Distribution
          </h3>
          <div className="flex h-1.5 w-full overflow-hidden bg-rule rounded-xs">
            {Object.entries(stats.source_type_distribution).map(([type, count], idx) => (
              <motion.div
                key={type}
                className={idx === 0 ? "bg-ember" : idx === 1 ? "bg-amber-note" : "bg-graphite"}
                initial={{ width: 0 }}
                animate={{ width: `${(count / totalSources) * 100}%` }}
                transition={{ duration: 0.5, delay: 0.1 }}
              />
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2">
            {Object.entries(stats.source_type_distribution).map(([type, count]) => (
              <p key={type} className="font-mono text-[12px] text-stone">
                {sourceLabel(type)}
                <span className="ml-2 font-medium text-ink">{count}</span>
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-12">
        <div>
          <h3 className="font-serif text-[17px] font-semibold text-ink tracking-tight mb-4">
            Confidence Breakdown
          </h3>
          <div className="space-y-3">
            {Object.entries(stats.confidence_distribution).map(([level, count]) => {
              const total = stats.decision_count || 1;
              const pct = Math.round((count / total) * 100);
              return (
                <div key={level} className="flex items-baseline justify-between text-[14px]">
                  <span className="capitalize text-stone">{level}</span>
                  <span className="font-mono text-[13px] text-ink">
                    {count}
                    <span className="ml-2 text-stone font-normal">{pct}%</span>
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <h3 className="font-serif text-[17px] font-semibold text-ink tracking-tight mb-4">
            Instruments & Engine
          </h3>
          <div className="space-y-3 text-[14px]">
            <div className="flex items-baseline justify-between">
              <span className="text-stone">Knowledge Graph (Neo4j)</span>
              <span className="font-mono text-[13px] font-medium text-ink">
                {stats.neo4j_connected ? "connected" : "offline"}
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-stone">Language Model (Ollama)</span>
              <span className="font-mono text-[13px] font-medium text-ink">
                {stats.llm_connected ? "connected" : "offline"}
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-stone">Target Repository</span>
              <span className="font-mono text-[13px] text-ink">{stats.repo}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
