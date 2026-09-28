"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, AlertCircle } from "lucide-react";
import Header from "@/components/layout/Header";
import StatsCards from "@/components/dashboard/StatsCards";
import GitLogo from "@/components/icons/GitLogo";
import { getStats, getGoldenQuestions, getDecisions } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { StatsResponse, GoldenQuestion, Decision } from "@/types/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [questions, setQuestions] = useState<GoldenQuestion[]>([]);
  const [recent, setRecent] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, questionsData] = await Promise.all([
          getStats(),
          getGoldenQuestions(),
        ]);
        setStats(statsData);
        setQuestions(questionsData.questions);

        try {
          const decisionsData = await getDecisions({ limit: 8 });
          setRecent(decisionsData.decisions);
        } catch {
          setRecent([]);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to connect to backend"
        );
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-grid">
      <Header
        title="Repository Briefing"
        description="Historical software decisions and architectural evidence"
      />

      <div className="px-8 sm:px-12 py-12 sm:py-16 max-w-4xl space-y-20">
        <motion.section
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
        >
          <div className="flex items-center gap-2.5">
            <GitLogo className="h-4 w-4 text-ember" />
            <span className="font-mono text-[13px] text-stone tracking-normal">
              {stats?.repo || "pallets/flask"}
            </span>
          </div>

          <h2 className="mt-4 font-serif text-3xl sm:text-[38px] sm:leading-[1.22] font-bold text-ink tracking-tight">
            Code tells you what.<br className="hidden sm:inline" /> History tells you why.
          </h2>

          <p className="mt-5 max-w-2xl text-[16px] leading-[1.75] text-stone">
            Reconstructs historical software decisions from GitHub discussions
            using an evidence-first retrieval pipeline and knowledge graph.
          </p>

          <div className="mt-8">
            <button
              onClick={() => router.push("/investigate")}
              className="group inline-flex items-center gap-2.5 border-b border-ink pb-1 text-[14px] font-medium text-ink transition-colors hover:border-ember hover:text-ember"
            >
              Open the investigation console
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" strokeWidth={1.5} />
            </button>
          </div>
        </motion.section>

        {error && (
          <div className="flex items-start gap-4 border-t border-rule pt-8">
            <AlertCircle className="h-5 w-5 text-ember flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div>
              <p className="text-[15px] font-medium text-ink">Backend connection error</p>
              <p className="text-[14px] text-stone mt-1.5 leading-relaxed">
                {error}. Make sure FastAPI is running on{" "}
                <code className="font-mono text-[13px] text-ink">
                  {process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}
                </code>
              </p>
            </div>
          </div>
        )}

        {recent.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <div className="mb-8">
              <h2 className="font-serif text-xl sm:text-[23px] font-semibold text-ink tracking-tight">
                Recent Discoveries
              </h2>
              <p className="mt-1 text-[14px] text-stone">
                Decisions extracted and contextualized from repository discussion threads
              </p>
            </div>

            <ol className="relative">
              {recent.map((d, idx) => (
                <li key={d.id} className="relative flex gap-5 pb-8 last:pb-0">
                  <div className="relative flex w-3 flex-col items-center">
                    <span
                      className={`mt-2 h-2 w-2 rounded-full ${
                        idx === 0 ? "bg-ember" : "bg-graphite"
                      }`}
                    />
                    {idx < recent.length - 1 && (
                      <span className="absolute top-4 bottom-0 w-px bg-rule" />
                    )}
                  </div>
                  <button
                    onClick={() =>
                      router.push(
                        `/investigate?q=${encodeURIComponent(d.summary)}`
                      )
                    }
                    className="flex-1 text-left group pt-0.5"
                  >
                    <p className="text-[16px] text-ink leading-snug font-medium group-hover:underline group-hover:underline-offset-4 decoration-rule">
                      {d.summary}
                    </p>
                    <p className="mt-2 font-mono text-[12px] text-stone">
                      {d.source_id ? `#${d.source_id}` : d.source_type}
                      {d.people?.[0] && ` · @${d.people[0]}`}
                      {d.dates?.[0] && ` · ${formatDate(d.dates[0])}`}
                    </p>
                  </button>
                </li>
              ))}
            </ol>
          </motion.section>
        )}

        {stats && !loading && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <StatsCards stats={stats} />
          </motion.section>
        )}

        {questions.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <div className="mb-8">
              <h2 className="font-serif text-xl sm:text-[23px] font-semibold text-ink tracking-tight">
                Try a Golden Question
              </h2>
              <p className="mt-1 text-[14px] text-stone">
                Curated architectural investigations tested against verified ground-truth rationale
              </p>
            </div>

            <ul className="divide-y divide-rule border-t border-b border-rule">
              {questions.slice(0, 6).map((q) => (
                <li key={q.id}>
                  <button
                    onClick={() =>
                      router.push(
                        `/investigate?q=${encodeURIComponent(q.question)}`
                      )
                    }
                    className="group flex w-full items-baseline gap-5 py-4 sm:py-5 text-left transition-colors hover:bg-surface/50 px-2 -mx-2"
                  >
                    <span className="font-mono text-[12px] text-stone w-7 shrink-0 font-medium">
                      {String(q.id).padStart(2, "0")}
                    </span>
                    <span className="flex-1 text-[15px] sm:text-[16px] text-ink leading-relaxed group-hover:text-ember transition-colors">
                      {q.question}
                    </span>
                    <ArrowRight
                      className="h-4 w-4 text-stone opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-1"
                      strokeWidth={1.5}
                    />
                  </button>
                </li>
              ))}
            </ul>
          </motion.section>
        )}
      </div>
    </div>
  );
}
