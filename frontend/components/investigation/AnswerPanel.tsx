"use client";

import { motion } from "framer-motion";
import {
  BookOpen,
  Box,
  Compass,
  FileCode,
  GitBranch,
  Layers,
  Sparkles,
} from "lucide-react";
import type { AskResponse } from "@/types/api";
import { formatDate } from "@/lib/utils";

interface AnswerPanelProps {
  data: AskResponse;
}

export default function AnswerPanel({ data }: AnswerPanelProps) {
  const category = data.category || "historical";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-10"
    >
      {/* ─── CATEGORY BADGE & CONFIDENCE BAR ─── */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          {category === "repository" && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-medium uppercase tracking-[0.14em] bg-ember/10 text-ember border border-ember/25 rounded-xs">
              <Layers className="h-3.5 w-3.5" />
              Repository Architecture
            </span>
          )}
          {category === "general" && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-medium uppercase tracking-[0.14em] bg-surface text-stone border border-rule rounded-xs">
              <BookOpen className="h-3.5 w-3.5" />
              Technical Concept
            </span>
          )}
          {category === "historical" && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-medium uppercase tracking-[0.14em] bg-amber-note/15 text-amber-note border border-amber-note/30 rounded-xs">
              <Compass className="h-3.5 w-3.5" />
              Historical Investigation
            </span>
          )}
          {category === "hybrid" && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-medium uppercase tracking-[0.14em] bg-ember/15 text-ember border border-ember/35 rounded-xs">
              <GitBranch className="h-3.5 w-3.5" />
              Hybrid Analysis
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 font-mono text-[12px] text-stone">
          <span className="capitalize">{data.confidence} confidence</span>
          <span className="text-rule-strong">·</span>
          <span className="text-ember font-medium uppercase tracking-wider">{data.mode}</span>
        </div>
      </div>

      {/* ─── DYNAMIC CATEGORY VIEWS ─── */}

      {/* 1. REPOSITORY ARCHITECTURE VIEW */}
      {category === "repository" && (
        <div className="space-y-12">
          {/* Main Answer Card */}
          <section className="bg-surface/80 border border-rule p-8 sm:p-10 shadow-xs space-y-6">
            <h2 className="font-serif text-2xl sm:text-[28px] font-semibold text-ink tracking-tight">
              Architecture & Execution Flow
            </h2>

            {data.overview && (
              <p className="font-serif text-[17px] sm:text-[18px] leading-[1.8] text-ink/90 italic border-l-2 border-ember pl-4 py-0.5">
                {data.overview}
              </p>
            )}

            <p className="font-sans text-[15px] sm:text-[16px] leading-[1.8] text-ink whitespace-pre-line">
              {data.answer}
            </p>
          </section>

          {/* Visual Architecture Flow Stepper */}
          {data.architecture_flow && data.architecture_flow.length > 0 && (
            <section className="bg-surface/50 border border-rule p-8 sm:p-10">
              <div className="mb-8">
                <h3 className="font-serif text-xl sm:text-[22px] font-semibold text-ink tracking-tight">
                  Request Execution Flow
                </h3>
                <p className="mt-1 text-[14px] text-stone">
                  Step-by-step traversal through pallets/flask runtime components
                </p>
              </div>

              <div className="relative pl-6 sm:pl-8 space-y-8">
                {/* Connecting timeline spine */}
                <div className="absolute left-[11px] sm:left-[15px] top-3 bottom-3 w-px bg-rule-strong" />

                {data.architecture_flow.map((step, idx) => (
                  <div key={step.title} className="relative group">
                    {/* Node indicator */}
                    <div className="absolute -left-[23px] sm:-left-[27px] top-1.5 h-3 w-3 rounded-full bg-surface border-2 border-ember group-hover:scale-125 transition-transform" />

                    <div className="space-y-1.5">
                      <div className="flex flex-wrap items-baseline gap-2.5">
                        <span className="font-mono text-[11px] text-stone font-semibold">
                          0{idx + 1}
                        </span>
                        <h4 className="font-serif text-[17px] font-medium text-ink">
                          {step.title}
                        </h4>
                        {step.component && (
                          <span className="font-mono text-[11px] text-stone px-2 py-0.5 bg-paper border border-rule rounded-xs">
                            {step.component}
                          </span>
                        )}
                        {step.file_path && (
                          <a
                            href={`https://github.com/pallets/flask/blob/main/${step.file_path}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 font-mono text-[11px] text-stone hover:text-ember transition-colors"
                          >
                            <FileCode className="h-3 w-3" />
                            {step.file_path}
                          </a>
                        )}
                      </div>
                      <p className="text-[14px] leading-relaxed text-stone max-w-3xl">
                        {step.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Key Modules Grid */}
          {data.key_modules && data.key_modules.length > 0 && (
            <section>
              <div className="mb-6">
                <h3 className="font-serif text-xl sm:text-[22px] font-semibold text-ink tracking-tight">
                  Core Architectural Modules
                </h3>
                <p className="mt-1 text-[14px] text-stone">
                  Primary subsystems and responsibility boundaries in the codebase
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.key_modules.map((mod) => (
                  <div
                    key={mod.name}
                    className="p-5 border border-rule bg-surface/70 hover:border-rule-strong transition-colors space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-mono text-[14px] font-medium text-ink">
                          {mod.name}
                        </p>
                        <p className="text-[11px] font-mono text-stone">
                          {mod.role}
                        </p>
                      </div>
                      <a
                        href={`https://github.com/pallets/flask/blob/main/${mod.file}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-[11px] text-stone hover:text-ember transition-colors shrink-0"
                      >
                        {mod.file}
                      </a>
                    </div>
                    <p className="text-[13px] text-stone leading-relaxed">
                      {mod.description}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Important Files */}
          {data.relevant_files && data.relevant_files.length > 0 && (
            <div className="pt-6 border-t border-rule">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                Important Code Files
              </p>
              <div className="flex flex-wrap gap-2">
                {data.relevant_files.map((file) => (
                  <a
                    key={file}
                    href={`https://github.com/pallets/flask/blob/main/${file}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1 font-mono text-[12px] bg-surface border border-rule text-ink hover:border-ember hover:text-ember transition-colors rounded-xs"
                  >
                    <FileCode className="h-3.5 w-3.5 text-stone" />
                    {file}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 2. GENERAL TECHNICAL CONCEPT VIEW */}
      {category === "general" && (
        <div className="space-y-10">
          <section className="bg-surface/80 border border-rule p-8 sm:p-10 shadow-xs space-y-6">
            <h2 className="font-serif text-2xl sm:text-[28px] font-semibold text-ink tracking-tight">
              Concept & Architecture
            </h2>

            {data.concept && (
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-stone">
                  Definition
                </p>
                <p className="font-serif text-[17px] sm:text-[18px] leading-[1.8] text-ink font-normal">
                  {data.concept}
                </p>
              </div>
            )}

            {data.how_it_works && (
              <div className="pt-6 border-t border-rule space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-stone">
                  How It Works
                </p>
                <p className="font-sans text-[15px] sm:text-[16px] leading-[1.8] text-ink">
                  {data.how_it_works}
                </p>
              </div>
            )}

            {!data.concept && !data.how_it_works && (
              <p className="font-serif text-[17px] sm:text-[18px] leading-[1.82] text-ink font-normal">
                {data.answer}
              </p>
            )}
          </section>

          {/* "Inside pallets/flask" Context Card */}
          {data.in_repository && (
            <section className="border border-rule bg-surface/50 p-8 sm:p-10 space-y-4">
              <div className="flex items-center gap-2">
                <Box className="h-4 w-4 text-ember" />
                <h3 className="font-serif text-lg font-semibold text-ink">
                  Inside pallets/flask
                </h3>
              </div>
              <p className="text-[15px] sm:text-[16px] leading-[1.8] text-ink">
                {data.in_repository}
              </p>

              {data.relevant_files && data.relevant_files.length > 0 && (
                <div className="pt-4 border-t border-rule/60">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-stone mb-2">
                    Relevant Repository Files
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {data.relevant_files.map((file) => (
                      <a
                        key={file}
                        href={`https://github.com/pallets/flask/blob/main/${file}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1 font-mono text-[12px] bg-paper border border-rule text-ink hover:text-ember transition-colors rounded-xs"
                      >
                        <FileCode className="h-3 w-3 text-stone" />
                        {file}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}
        </div>
      )}

      {/* 3. HISTORICAL / WHY VIEW */}
      {category === "historical" && (
        <section className="bg-surface/70 border border-rule p-8 sm:p-10 shadow-xs">
          <div className="flex flex-wrap items-baseline justify-between gap-4 mb-6 pb-4 border-b border-rule">
            <h2 className="font-serif text-xl sm:text-2xl font-semibold text-ink tracking-tight">
              Synthesized Rationale
            </h2>
          </div>

          <p className="font-serif text-[17px] sm:text-[18px] leading-[1.82] text-ink font-normal">
            {data.answer}
          </p>

          {(data.people.length > 0 || data.dates.length > 0 || data.sources.length > 0) && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-8 mt-8 border-t border-rule">
              {data.people.length > 0 && (
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                    Key Contributors
                  </p>
                  <div className="space-y-1.5">
                    {data.people.map((person) => (
                      <a
                        key={person}
                        href={`https://github.com/${person}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block font-mono text-[13px] text-ink hover:text-ember transition-colors"
                      >
                        @{person}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {data.dates.length > 0 && (
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                    Historical Timeline
                  </p>
                  <div className="space-y-1.5">
                    {data.dates.map((date) => (
                      <p key={date} className="font-mono text-[13px] text-ink">
                        {formatDate(date)}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {data.sources.length > 0 && (
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                    Discussion Sources
                  </p>
                  <div className="space-y-1.5">
                    {data.sources.map((url) => {
                      const shortUrl = url.replace(
                        "https://github.com/pallets/flask/",
                        ""
                      );
                      return (
                        <a
                          key={url}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block font-mono text-[13px] text-ink hover:text-ember transition-colors truncate"
                        >
                          {shortUrl}
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {data.relevant_files && data.relevant_files.length > 0 && (
            <div className="pt-6 mt-8 border-t border-rule">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-2">
                Associated Code Files
              </p>
              <div className="flex flex-wrap gap-2">
                {data.relevant_files.map((file) => (
                  <a
                    key={file}
                    href={`https://github.com/pallets/flask/blob/main/${file}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-2.5 py-0.5 font-mono text-[12px] bg-paper border border-rule text-stone hover:text-ember transition-colors rounded-xs"
                  >
                    <FileCode className="h-3 w-3" />
                    {file}
                  </a>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* 4. HYBRID VIEW */}
      {category === "hybrid" && (
        <div className="space-y-10">
          <section className="bg-surface/80 border border-rule p-8 sm:p-10 shadow-xs space-y-6">
            <h2 className="font-serif text-2xl sm:text-[28px] font-semibold text-ink tracking-tight">
              Architecture & Historical Evolution
            </h2>

            {data.overview && (
              <p className="font-serif text-[17px] sm:text-[18px] leading-[1.8] text-ink/90 italic border-l-2 border-ember pl-4 py-0.5">
                {data.overview}
              </p>
            )}

            <p className="font-sans text-[15px] sm:text-[16px] leading-[1.8] text-ink whitespace-pre-line">
              {data.answer}
            </p>

            {(data.people.length > 0 || data.dates.length > 0) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 pt-8 border-t border-rule">
                {data.people.length > 0 && (
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                      Key Contributors
                    </p>
                    <div className="space-y-1.5">
                      {data.people.map((person) => (
                        <a
                          key={person}
                          href={`https://github.com/${person}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block font-mono text-[13px] text-ink hover:text-ember transition-colors"
                        >
                          @{person}
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {data.dates.length > 0 && (
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone mb-3">
                      Timeline
                    </p>
                    <div className="space-y-1.5">
                      {data.dates.map((date) => (
                        <p key={date} className="font-mono text-[13px] text-ink">
                          {formatDate(date)}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Key Modules if available */}
          {data.key_modules && data.key_modules.length > 0 && (
            <div className="space-y-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone">
                Underlying Modules
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.key_modules.map((mod) => (
                  <div key={mod.name} className="p-4 border border-rule bg-surface">
                    <p className="font-mono text-[13px] font-medium text-ink">{mod.name}</p>
                    <p className="text-[12px] text-stone mt-1">{mod.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
