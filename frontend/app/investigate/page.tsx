"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import Header from "@/components/layout/Header";
import SearchBar from "@/components/investigation/SearchBar";
import AnswerPanel from "@/components/investigation/AnswerPanel";
import EvidenceCard from "@/components/investigation/EvidenceCard";
import GraphPath from "@/components/investigation/GraphPath";
import { SkeletonAnswer } from "@/components/ui/Skeleton";
import { askQuestion, getGoldenQuestions } from "@/lib/api";
import type { AskResponse, GoldenQuestion } from "@/types/api";

function InvestigateContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    getGoldenQuestions()
      .then((data) =>
        setSuggestions(data.questions.map((q: GoldenQuestion) => q.question))
      )
      .catch(() => {});
  }, []);

  const handleInvestigate = useCallback(async (question: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const url = new URL(window.location.href);
    url.searchParams.set("q", question);
    window.history.replaceState({}, "", url.toString());

    try {
      const data = await askQuestion({ question, top_k: 5 });
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get an answer. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialQuery) {
      handleInvestigate(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-grid">
      <Header
        title="Investigate"
        description="Query the repository why-code history and architectural rationale"
      />

      <div className="px-8 sm:px-12 py-12 sm:py-16 max-w-4xl space-y-16">
        <SearchBar
          onSubmit={handleInvestigate}
          isLoading={loading}
          initialQuery={initialQuery}
          suggestions={suggestions}
        />

        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="pt-4">
            <p className="font-mono text-[13px] text-stone mb-8 flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-ember animate-pulse" />
              Retrieving evidence trail and synthesizing answer…
            </p>
            <SkeletonAnswer />
          </motion.div>
        )}

        {error && (
          <div className="flex items-start gap-4 border-t border-rule pt-8">
            <AlertCircle className="h-5 w-5 text-ember flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div>
              <p className="text-[15px] font-medium text-ink">Investigation failed</p>
              <p className="text-[14px] text-stone mt-1.5 leading-relaxed">{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-16">
            <AnswerPanel data={result} />

            {result.graph_path.length > 0 && (
              <div>
                <hr className="section-rule mb-12" />
                <GraphPath path={result.graph_path} />
              </div>
            )}

            {result.evidence.length > 0 && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.15 }}
              >
                <hr className="section-rule mb-12" />
                <div className="mb-8">
                  <h2 className="font-serif text-xl sm:text-[23px] font-semibold text-ink tracking-tight">
                    Evidence Trail
                  </h2>
                  <p className="mt-1 font-mono text-[12px] text-stone">
                    {result.evidence.length} primary source{result.evidence.length !== 1 ? "s" : ""} retrieved & verified
                  </p>
                </div>
                <div className="divide-y divide-rule border-b border-rule">
                  {result.evidence.map((evidence, idx) => (
                    <EvidenceCard
                      key={evidence.decision_id}
                      evidence={evidence}
                      index={idx}
                    />
                  ))}
                </div>
              </motion.section>
            )}

            {result.evidence.length === 0 && result.mode === "fallback" && (
              <p className="text-[15px] leading-relaxed text-stone border-t border-rule pt-10">
                No strong evidence was found for this question. Try rephrasing
                or asking about a specific Flask feature or design decision.
              </p>
            )}
          </div>
        )}

        {!loading && !result && !error && (
          <div className="py-20 border-t border-rule">
            <h2 className="font-serif text-2xl font-bold text-ink tracking-tight">
              Ask a question about pallets/flask
            </h2>
            <p className="mt-3 max-w-lg text-[15px] leading-[1.75] text-stone">
              CodeArchaeologist navigates historical GitHub discussions, issues, commits,
              and pull requests to explain the reasoning behind architectural choices.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function InvestigatePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-grid">
          <Header
            title="Investigate"
            description="Query the repository why-code history and architectural rationale"
          />
          <div className="px-8 sm:px-12 py-12 sm:py-16 max-w-4xl">
            <SkeletonAnswer />
          </div>
        </div>
      }
    >
      <InvestigateContent />
    </Suspense>
  );
}
