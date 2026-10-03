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
import ChatInterface from "@/components/chat/ChatInterface";
import { Sparkles, Search as SearchIcon } from "lucide-react";

// ─── Example question categories shown in the empty state ───────────────────

const QUESTION_CATEGORIES = [
  {
    label: "Historical · Why",
    accent: "#d4622a",
    icon: "📜",
    description: "Trace the reasoning behind code decisions",
    questions: [
      "Why was request.json deprecated?",
      "Why was Flask's before_request hook introduced?",
      "Why did Flask move to Blueprints?",
      "Why was the ApplicationContext separated?",
    ],
  },
  {
    label: "Repository · Architecture",
    accent: "#4db6ac",
    icon: "🏛",
    description: "Explore the structure of pallets/flask",
    questions: [
      "What is the architecture of Flask?",
      "How does the request lifecycle work?",
      "Where is routing handled in Flask?",
      "What are the major modules in Flask?",
    ],
  },
  {
    label: "General · Concepts",
    accent: "#9575cd",
    icon: "💡",
    description: "Understand web concepts, grounded in this repo",
    questions: [
      "What is WSGI?",
      "What is middleware?",
      "What is a request context?",
      "What is dependency injection?",
    ],
  },
] as const;

// ─── Empty-state question showcase ──────────────────────────────────────────

function QuestionShowcase({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="border-t border-rule pt-14 space-y-12"
    >
      <div>
        <h2 className="font-serif text-2xl font-bold text-ink tracking-tight">
          Ask anything about{" "}
          <span style={{ color: "var(--color-ember)" }}>pallets/flask</span>
        </h2>
        <p className="mt-2 text-[14px] leading-[1.75] text-stone max-w-lg">
          From architectural decisions to concept explanations — every answer is
          grounded in the actual repository, its history and its code.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
        {QUESTION_CATEGORIES.map((cat, catIdx) => (
          <motion.div
            key={cat.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * catIdx, duration: 0.35 }}
            className="space-y-4"
          >
            {/* Category header */}
            <div className="flex items-start gap-2.5 pb-3 border-b border-rule">
              <span className="text-[18px] leading-none mt-0.5">{cat.icon}</span>
              <div>
                <p
                  className="font-mono text-[10px] font-semibold tracking-widest uppercase"
                  style={{ color: cat.accent }}
                >
                  {cat.label}
                </p>
                <p className="text-[11px] text-stone leading-tight mt-0.5">
                  {cat.description}
                </p>
              </div>
            </div>

            {/* Clickable question chips */}
            <ul className="space-y-1.5">
              {cat.questions.map((q) => (
                <li key={q}>
                  <button
                    onClick={() => onSelect(q)}
                    className="w-full text-left group"
                  >
                    <span
                      className="block text-[13px] leading-[1.55] text-stone transition-all duration-150
                        group-hover:text-ink rounded px-2.5 py-1.5 -mx-2.5
                        border border-transparent group-hover:border-rule
                        group-hover:bg-white/5"
                    >
                      {q}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

// ─── Main page content ───────────────────────────────────────────────────────

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

  const [activeTab, setActiveTab] = useState<"investigate" | "chat">("investigate");

  return (
    <div className="min-h-screen bg-grid">
      <Header
        title={activeTab === "chat" ? "AI Conversation" : "Investigate"}
        description={
          activeTab === "chat"
            ? "Multi-turn conversational code archaeology & general programming assistant powered by Sarvam AI"
            : "Ask why, what, how, or where — grounded in the actual repository"
        }
      />

      <div className="px-8 sm:px-12 py-8 max-w-4xl space-y-10">
        {/* Tab Switcher */}
        <div className="flex items-center gap-2 border-b border-rule pb-4">
          <button
            onClick={() => setActiveTab("investigate")}
            className={`flex items-center gap-2 px-3.5 py-1.5 font-mono text-xs transition-colors rounded-xs border ${
              activeTab === "investigate"
                ? "bg-ink text-paper border-ink font-semibold shadow-xs"
                : "bg-surface text-stone border-rule hover:text-ink"
            }`}
          >
            <SearchIcon className="h-3.5 w-3.5" />
            <span>Deep Investigation</span>
          </button>

          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center gap-2 px-3.5 py-1.5 font-mono text-xs transition-colors rounded-xs border ${
              activeTab === "chat"
                ? "bg-ink text-paper border-ink font-semibold shadow-xs"
                : "bg-surface text-stone border-rule hover:text-ink"
            }`}
          >
            <Sparkles className="h-3.5 w-3.5 text-ember" />
            <span>AI Conversation (Sarvam AI)</span>
          </button>
        </div>

        {activeTab === "chat" ? (
          <div className="h-[calc(100vh-240px)] flex flex-col min-h-0">
            <ChatInterface />
          </div>
        ) : (
          <div className="space-y-16">
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
                    {result.evidence.length} primary source
                    {result.evidence.length !== 1 ? "s" : ""} retrieved &amp; verified
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
              <QuestionShowcase onSelect={handleInvestigate} />
            )}
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
            description="Ask why, what, how, or where — grounded in the actual repository"
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
