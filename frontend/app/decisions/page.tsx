"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import Header from "@/components/layout/Header";
import DecisionCard from "@/components/decisions/DecisionCard";
import { getDecisions } from "@/lib/api";
import { yearFromDate } from "@/lib/utils";
import type { Decision } from "@/types/api";

const CONFIDENCE_OPTIONS = ["all", "high", "medium", "low"] as const;
const SOURCE_TYPE_OPTIONS = [
  { value: "all", label: "All sources" },
  { value: "github_pr", label: "Pull Requests" },
  { value: "github_issue", label: "Issues" },
  { value: "github_commit", label: "Commits" },
];

function groupByYear(decisions: Decision[]) {
  const groups = new Map<string, Decision[]>();
  for (const decision of decisions) {
    const year = yearFromDate(decision.dates?.[0]);
    const list = groups.get(year) ?? [];
    list.push(decision);
    groups.set(year, list);
  }

  return Array.from(groups.entries()).sort((a, b) => {
    if (a[0] === "Undated") return 1;
    if (b[0] === "Undated") return -1;
    return Number(b[0]) - Number(a[0]);
  });
}

export default function DecisionsPage() {
  const router = useRouter();
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confidenceFilter, setConfidenceFilter] = useState<string>("all");
  const [sourceFilter, setSourceFilter] = useState<string>("all");

  useEffect(() => {
    async function fetchDecisions() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDecisions({
          confidence: confidenceFilter === "all" ? undefined : confidenceFilter,
          source_type: sourceFilter === "all" ? undefined : sourceFilter,
          limit: 100,
        });
        setDecisions(data.decisions);
        setTotal(data.total);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load decisions"
        );
      } finally {
        setLoading(false);
      }
    }
    fetchDecisions();
  }, [confidenceFilter, sourceFilter]);

  const grouped = useMemo(() => groupByYear(decisions), [decisions]);

  return (
    <div className="min-h-screen bg-grid">
      <Header
        title="Decision Archive"
        description="Catalog of verified architectural decisions reconstructed from repository history"
      />

      <div className="px-8 sm:px-12 py-12 sm:py-16 max-w-4xl">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-wrap items-center justify-between gap-6 mb-16 pb-6 border-b border-rule"
        >
          <div className="flex items-center gap-1 border-b border-rule sm:border-b-0">
            {CONFIDENCE_OPTIONS.map((opt) => (
              <button
                key={opt}
                onClick={() => setConfidenceFilter(opt)}
                className={`px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
                  confidenceFilter === opt
                    ? "text-ink border-b-2 border-ember -mb-px"
                    : "text-stone hover:text-ink"
                }`}
              >
                {opt === "all" ? "All" : opt.charAt(0).toUpperCase() + opt.slice(1)}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <span className="font-mono text-[13px] text-stone">
              {total} decision{total !== 1 ? "s" : ""}
            </span>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="border border-rule bg-surface px-3 py-1.5 text-[13px] text-ink outline-none"
            >
              {SOURCE_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </motion.div>

        {loading && (
          <div className="py-20 text-center">
            <p className="font-mono text-[13px] text-stone">Loading decision archive…</p>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-4 border border-rule bg-surface p-6 mb-12">
            <AlertCircle className="h-5 w-5 text-ember flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div>
              <p className="text-[15px] font-medium text-ink">Failed to load decisions</p>
              <p className="text-[14px] text-stone mt-1">{error}</p>
            </div>
          </div>
        )}

        {!loading && decisions.length === 0 && !error && (
          <div className="py-20 text-center">
            <p className="font-serif text-xl font-semibold text-ink">No decisions match this filter</p>
            <p className="text-[14px] text-stone mt-2">Try clearing your filters to see more results</p>
          </div>
        )}

        {!loading && decisions.length > 0 && (
          <div className="space-y-16">
            {grouped.map(([year, items]) => (
              <motion.section
                key={year}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.45, ease: "easeOut" }}
              >
                <div className="flex items-baseline justify-between border-b border-rule pb-3 mb-6">
                  <h2 className="font-serif text-2xl font-bold text-ink tracking-tight">
                    {year}
                  </h2>
                  <span className="font-mono text-[12px] text-stone">
                    {items.length} decision{items.length !== 1 ? "s" : ""}
                  </span>
                </div>

                <div className="divide-y divide-rule border-b border-rule">
                  {items.map((decision, idx) => (
                    <DecisionCard
                      key={decision.id}
                      decision={decision}
                      index={idx}
                      onClick={() =>
                        router.push(
                          `/investigate?q=${encodeURIComponent(decision.summary)}`
                        )
                      }
                    />
                  ))}
                </div>
              </motion.section>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
