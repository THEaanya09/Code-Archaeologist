"use client";

import { motion } from "framer-motion";
import type { AskResponse } from "@/types/api";
import { formatDate } from "@/lib/utils";

interface AnswerPanelProps {
  data: AskResponse;
}

export default function AnswerPanel({ data }: AnswerPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-10"
    >
      <section className="bg-surface/70 border border-rule p-8 sm:p-10 shadow-xs">
        <div className="flex flex-wrap items-baseline justify-between gap-4 mb-6 pb-4 border-b border-rule">
          <h2 className="font-serif text-xl sm:text-2xl font-semibold text-ink tracking-tight">
            Synthesized Rationale
          </h2>
          <div className="flex items-center gap-3 font-mono text-[12px] text-stone">
            <span className="capitalize">{data.confidence} confidence</span>
            <span className="text-rule-strong">·</span>
            <span className="text-ember font-medium uppercase tracking-wider">{data.mode}</span>
          </div>
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
      </section>
    </motion.div>
  );
}
