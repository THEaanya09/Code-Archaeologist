"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  RotateCcw,
  Sparkles,
  Layers,
  BookOpen,
  Zap,
  Check,
  Copy,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  FileCode,
  Info,
} from "lucide-react";
import type { ChatMessage, ChatMode, ChatResponse, Evidence } from "@/types/api";
import { sendChatMessage, clearChatSession, getChatSession } from "@/lib/api";

// ─── Preset suggestions ──────────────────────────────────────────

const PROMPT_SUGGESTIONS: { text: string; mode: ChatMode; tag: string }[] = [
  {
    text: "Why was request.json deprecated in Flask?",
    mode: "repository",
    tag: "Repository Why",
  },
  {
    text: "Explain how Flask handles the WSGI application dispatch cycle.",
    mode: "repository",
    tag: "Architecture",
  },
  {
    text: "Write a production-grade Python decorator with TTL caching and arguments support.",
    mode: "general",
    tag: "Python Code",
  },
  {
    text: "What is the difference between WSGI and ASGI in modern Python web frameworks?",
    mode: "general",
    tag: "Concepts",
  },
  {
    text: "Why did Flask separate ApplicationContext from RequestContext in 0.9?",
    mode: "auto",
    tag: "Auto Route",
  },
];

// ─── Markdown Renderer ───────────────────────────────────────────

function CodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  return (
    <div className="my-4 rounded-xs border border-rule bg-charcoal/5 dark:bg-surface overflow-hidden text-sm">
      <div className="flex items-center justify-between px-4 py-1.5 border-b border-rule bg-paper/60 font-mono text-[11px] text-stone">
        <span>{language || "code"}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 hover:text-ink transition-colors px-2 py-0.5 rounded-xs"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-ember" />
              <span className="text-ember font-medium">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto font-mono text-[13px] leading-relaxed text-ink">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function FormattedContent({ text }: { text: string }) {
  if (!text) return null;

  // Split by code fences
  const parts = text.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-3 font-sans text-[15px] leading-[1.8] text-ink">
      {parts.map((part, idx) => {
        if (part.startsWith("```") && part.endsWith("```")) {
          const lines = part.slice(3, -3).trim().split("\n");
          const firstLine = lines[0]?.trim() || "";
          const isLanguageTag = /^[a-zA-Z0-9_+-]+$/.test(firstLine);
          const language = isLanguageTag ? firstLine : "";
          const code = isLanguageTag ? lines.slice(1).join("\n") : lines.join("\n");
          return <CodeBlock key={idx} code={code} language={language} />;
        }

        // Render standard paragraphs with markdown formatting
        const paragraphs = part.split(/\n\n+/);
        return (
          <div key={idx} className="space-y-3">
            {paragraphs.map((p, pIdx) => {
              const trimmed = p.trim();
              if (!trimmed) return null;

              // Headings
              if (trimmed.startsWith("### ")) {
                return (
                  <h4 key={pIdx} className="font-serif text-[17px] font-bold text-ink mt-4 mb-2">
                    {trimmed.replace(/^###\s+/, "")}
                  </h4>
                );
              }
              if (trimmed.startsWith("## ")) {
                return (
                  <h3 key={pIdx} className="font-serif text-[19px] font-bold text-ink mt-5 mb-2 border-b border-rule pb-1">
                    {trimmed.replace(/^##\s+/, "")}
                  </h3>
                );
              }

              // Bullet list items
              if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
                const items = trimmed.split(/\n[-*]\s+/).filter(Boolean);
                return (
                  <ul key={pIdx} className="list-disc pl-5 space-y-1.5 text-stone dark:text-stone/90">
                    {items.map((it, itIdx) => (
                      <li key={itIdx}>
                        <span className="text-ink">{it.replace(/^[-*]\s+/, "")}</span>
                      </li>
                    ))}
                  </ul>
                );
              }

              // Numbered list items
              if (/^\d+\.\s+/.test(trimmed)) {
                const items = trimmed.split(/\n(?=\d+\.\s+)/).filter(Boolean);
                return (
                  <ol key={pIdx} className="list-decimal pl-5 space-y-1.5 text-stone dark:text-stone/90">
                    {items.map((it, itIdx) => (
                      <li key={itIdx}>
                        <span className="text-ink">{it.replace(/^\d+\.\s+/, "")}</span>
                      </li>
                    ))}
                  </ol>
                );
              }

              // Blockquotes
              if (trimmed.startsWith("> ")) {
                return (
                  <blockquote
                    key={pIdx}
                    className="border-l-2 border-ember pl-4 py-1 italic text-stone bg-ember/5 my-2"
                  >
                    {trimmed.replace(/^>\s*/gm, "")}
                  </blockquote>
                );
              }

              return (
                <p key={pIdx} className="leading-relaxed whitespace-pre-wrap">
                  {trimmed}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ─── Evidence & Sources Accordion ────────────────────────────────

function SourcesDrawer({
  sources,
  evidence,
  relevantFiles,
}: {
  sources: string[];
  evidence: Evidence[];
  relevantFiles?: string[];
}) {
  const [open, setOpen] = useState(false);

  if (sources.length === 0 && evidence.length === 0 && (!relevantFiles || relevantFiles.length === 0)) {
    return null;
  }

  return (
    <div className="mt-4 pt-3 border-t border-rule">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-[12px] font-mono font-medium text-stone hover:text-ink transition-colors"
      >
        <Sparkles className="h-3.5 w-3.5 text-ember" />
        <span>
          Grounding Evidence ({evidence.length} decision{evidence.length !== 1 ? "s" : ""}, {sources.length} source{sources.length !== 1 ? "s" : ""})
        </span>
        {open ? <ChevronUp className="h-3.5 w-3.5 ml-1" /> : <ChevronDown className="h-3.5 w-3.5 ml-1" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden space-y-4 pt-3 text-xs"
          >
            {/* Relevant files */}
            {relevantFiles && relevantFiles.length > 0 && (
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone mb-1.5 flex items-center gap-1">
                  <FileCode className="h-3 w-3" /> Relevant Files
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {relevantFiles.map((file) => (
                    <span
                      key={file}
                      className="px-2 py-0.5 font-mono text-[11px] bg-rule/50 text-ink rounded-xs border border-rule"
                    >
                      {file}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence items */}
            {evidence.length > 0 && (
              <div className="space-y-2">
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone">Primary Evidence</p>
                <div className="space-y-2">
                  {evidence.map((ev) => (
                    <div
                      key={ev.decision_id}
                      className="p-2.5 rounded-xs border border-rule bg-surface/70 space-y-1"
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="text-ember font-semibold">[{ev.decision_id}]</span>
                        <span className="text-stone capitalize">{ev.confidence} confidence</span>
                      </div>
                      <p className="font-medium text-ink text-[12px]">{ev.summary}</p>
                      {ev.rationale && (
                        <p className="text-stone text-[11px] leading-relaxed italic">{ev.rationale}</p>
                      )}
                      {ev.source_url && (
                        <a
                          href={ev.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-ember hover:underline font-mono mt-1"
                        >
                          <span>View Source</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Source links */}
            {sources.length > 0 && (
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone mb-1">Source URLs</p>
                <ul className="space-y-1">
                  {sources.map((s, idx) => (
                    <li key={idx}>
                      <a
                        href={s}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-stone hover:text-ember transition-colors font-mono text-[11px] truncate flex items-center gap-1.5"
                      >
                        <ExternalLink className="h-3 w-3 shrink-0" />
                        <span className="truncate">{s}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── Main Chat Component ─────────────────────────────────────────

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ChatMode>("auto");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>("");
  const [remainingRequests, setRemainingRequests] = useState<number | null>(null);
  const [totalTokens, setTotalTokens] = useState<number>(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Initialize or restore session ID
  useEffect(() => {
    let sid = "";
    try {
      sid = localStorage.getItem("archaeologist_chat_session") || "";
    } catch {
      // ignore
    }
    if (!sid) {
      sid = "session_" + Math.random().toString(36).substring(2, 10);
      try {
        localStorage.setItem("archaeologist_chat_session", sid);
      } catch {
        // ignore
      }
    }
    setSessionId(sid);

    // Fetch existing session stats
    getChatSession(sid)
      .then((info) => {
        if (info.remaining_requests !== undefined) {
          setRemainingRequests(info.remaining_requests);
        }
        if (info.total_tokens_used !== undefined) {
          setTotalTokens(info.total_tokens_used);
        }
      })
      .catch(() => {});
  }, []);

  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  // Handle clearing conversation
  const handleClear = async () => {
    if (!sessionId) return;
    try {
      await clearChatSession(sessionId);
      setMessages([]);
      setError(null);
    } catch {
      setMessages([]);
    }
  };

  // Submit question
  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setError(null);

    const userMsgId = "msg_" + Date.now();
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: q,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res: ChatResponse = await sendChatMessage({
        question: q,
        mode,
        session_id: sessionId,
      });

      if (res.error) {
        setError(res.error);
      }

      if (res.remaining_requests !== undefined && res.remaining_requests !== null) {
        setRemainingRequests(res.remaining_requests);
      }

      if (res.usage?.total_tokens) {
        setTotalTokens((prev) => prev + (res.usage?.total_tokens || 0));
      }

      const assistantMsg: ChatMessage = {
        id: "msg_ast_" + Date.now(),
        role: "assistant",
        content: res.answer || (res.error ? `Error: ${res.error}` : "No response generated."),
        mode_used: res.mode_used,
        category: res.category,
        confidence: res.confidence,
        sources: res.sources,
        evidence: res.evidence,
        relevant_files: res.relevant_files,
        timestamp: Date.now(),
        usage: res.usage,
        error: res.error,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to communicate with AI chat service.";
      setError(errorMsg);
      const errorResponseMsg: ChatMessage = {
        id: "msg_err_" + Date.now(),
        role: "assistant",
        content: `Error: ${errorMsg}`,
        timestamp: Date.now(),
        error: errorMsg,
      };
      setMessages((prev) => [...prev, errorResponseMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 h-full max-w-4xl mx-auto w-full">
      {/* ─── Session Bar & Mode Selector ─── */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 mb-4 border-b border-rule shrink-0">
        {/* Mode selector pills */}
        <div className="flex items-center gap-1.5 p-1 bg-surface border border-rule rounded-xs">
          <button
            onClick={() => setMode("auto")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono transition-colors rounded-xs ${
              mode === "auto"
                ? "bg-ink text-paper font-semibold shadow-xs"
                : "text-stone hover:text-ink"
            }`}
          >
            <Zap className="h-3.5 w-3.5 text-amber-note" />
            <span>Auto</span>
          </button>

          <button
            onClick={() => setMode("repository")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono transition-colors rounded-xs ${
              mode === "repository"
                ? "bg-ink text-paper font-semibold shadow-xs"
                : "text-stone hover:text-ink"
            }`}
          >
            <Layers className="h-3.5 w-3.5 text-ember" />
            <span>Repository Analysis</span>
          </button>

          <button
            onClick={() => setMode("general")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono transition-colors rounded-xs ${
              mode === "general"
                ? "bg-ink text-paper font-semibold shadow-xs"
                : "text-stone hover:text-ink"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5 text-indigo-400" />
            <span>General AI</span>
          </button>
        </div>

        {/* Stats & Actions */}
        <div className="flex items-center gap-4 text-xs font-mono text-stone">
          {remainingRequests !== null && (
            <span className="flex items-center gap-1" title="Daily quota for dev mode">
              <span className="h-2 w-2 rounded-full bg-ember" />
              <span>{remainingRequests} req left</span>
            </span>
          )}

          {totalTokens > 0 && (
            <span className="text-stone/80">
              {totalTokens.toLocaleString()} tokens
            </span>
          )}

          {messages.length > 0 && (
            <button
              onClick={handleClear}
              className="flex items-center gap-1 text-stone hover:text-ember transition-colors py-1 px-2 border border-transparent hover:border-rule rounded-xs"
              title="Reset conversation"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* ─── Chat Message Scroll Area ─── */}
      <div
        ref={scrollContainerRef}
        data-lenis-prevent
        className="flex-1 min-h-0 overflow-y-auto overscroll-y-contain touch-pan-y space-y-6 pr-2 mb-4"
      >
        {messages.length === 0 ? (
          <div className="py-12 space-y-8">
            <div className="text-center space-y-3 max-w-md mx-auto">
              <div className="inline-flex p-3 rounded-full bg-ember/10 border border-ember/20 text-ember mb-2">
                <Sparkles className="h-6 w-6" />
              </div>
              <h3 className="font-serif text-2xl font-bold text-ink tracking-tight">
                Conversational Code Archaeologist
              </h3>
              <p className="text-[14px] leading-relaxed text-stone">
                Ask multi-turn questions about repository architecture, git commit history,
                design decisions, or general programming queries powered by{" "}
                <span className="font-semibold text-ember">Sarvam AI (sarvam-105b)</span>.
              </p>
            </div>

            {/* Preset prompt pills */}
            <div className="max-w-2xl mx-auto space-y-2">
              <p className="font-mono text-[11px] uppercase tracking-wider text-stone/80 mb-2">
                Suggested Starters
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {PROMPT_SUGGESTIONS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setMode(item.mode);
                      setInput(item.text);
                      textareaRef.current?.focus();
                    }}
                    className="p-3 text-left border border-rule bg-surface/60 hover:bg-surface hover:border-rule-strong transition-all rounded-xs group flex flex-col justify-between"
                  >
                    <span className="text-[13px] text-ink/90 group-hover:text-ink leading-snug">
                      {item.text}
                    </span>
                    <span className="mt-2 font-mono text-[10px] text-stone group-hover:text-ember flex items-center gap-1 uppercase tracking-wider">
                      <span>{item.tag}</span>
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === "user";

            return (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                {/* Role header */}
                <div className="flex items-center gap-2 mb-1 px-1 font-mono text-[11px] text-stone">
                  {isUser ? (
                    <span>You</span>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-ember">Archaeologist AI</span>
                      {msg.mode_used && (
                        <span className="px-1.5 py-0.5 rounded-xs bg-rule/50 text-[10px] uppercase tracking-wider">
                          {msg.mode_used}
                        </span>
                      )}
                      {msg.confidence && (
                        <span className="text-[10px] text-stone capitalize">
                          · {msg.confidence}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Message bubble */}
                <div
                  className={`max-w-[92%] sm:max-w-[85%] rounded-xs p-4 sm:p-5 border ${
                    isUser
                      ? "bg-surface border-rule-strong text-ink shadow-xs"
                      : "bg-surface/90 border-rule text-ink shadow-xs"
                  }`}
                >
                  <FormattedContent text={msg.content} />

                  {/* Sources / Evidence drawer for assistant messages */}
                  {!isUser && (
                    <SourcesDrawer
                      sources={msg.sources || []}
                      evidence={msg.evidence || []}
                      relevantFiles={msg.relevant_files}
                    />
                  )}

                  {/* Usage metadata footer */}
                  {!isUser && msg.usage?.total_tokens && (
                    <div className="mt-3 pt-2 border-t border-rule/60 flex items-center justify-between font-mono text-[10px] text-stone/80">
                      <span>{msg.usage.total_tokens} tokens</span>
                      <span>Sarvam 105B</span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })
        )}

        {/* Loading indicator */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-start gap-3 p-4 border border-rule bg-surface/50 rounded-xs"
          >
            <div className="h-4 w-4 rounded-full border-2 border-ember border-t-transparent animate-spin shrink-0 mt-0.5" />
            <div className="space-y-1 font-mono text-xs text-stone">
              <p className="text-ink font-medium">Synthesizing response…</p>
              <p className="text-[11px]">
                {mode === "repository"
                  ? "Querying Neo4j GraphRAG and analyzing commit evidence"
                  : mode === "general"
                  ? "Querying Sarvam AI 105B model"
                  : "Routing query and evaluating context"}
              </p>
            </div>
          </motion.div>
        )}

        {error && (
          <div className="p-3 border border-ember/30 bg-ember/10 rounded-xs text-xs flex items-center gap-2 text-ink">
            <AlertCircle className="h-4 w-4 text-ember shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ─── Fixed Bottom Input Form ─── */}
      <div className="pt-2 border-t border-rule shrink-0">
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2 bg-surface border border-rule focus-within:border-rule-strong p-2 rounded-xs shadow-xs">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === "repository"
                ? "Ask about Flask's commits, architecture, or design choices… (Enter to send)"
                : mode === "general"
                ? "Ask any programming or technology question… (Enter to send)"
                : "Ask any question (auto-routed to repo or general AI)… (Enter to send)"
            }
            rows={2}
            className="w-full resize-none bg-transparent font-sans text-[14px] leading-relaxed text-ink placeholder:text-stone/70 focus:outline-hidden p-1.5"
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-2.5 bg-ember text-white rounded-xs hover:bg-ember/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all shrink-0"
            title="Send message (Enter)"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>

        <div className="flex items-center justify-between px-1 pt-2 font-mono text-[11px] text-stone">
          <span>Shift + Enter for new line</span>
          <span className="flex items-center gap-1.5">
            <Info className="h-3 w-3" />
            <span>Powered by Sarvam AI · GraphRAG Grounded</span>
          </span>
        </div>
      </div>
    </div>
  );
}
