"use client";

import { AlertCircle, RotateCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <div className="max-w-md">
        <AlertCircle className="h-5 w-5 text-ember mb-4" strokeWidth={1.5} />
        <h2 className="text-[17px] font-medium text-ink mb-2">
          Something went wrong
        </h2>
        <p className="text-[14px] text-stone mb-6 leading-relaxed">
          {error.message ||
            "An unexpected error occurred. This might be a connection issue with the backend."}
        </p>
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 bg-charcoal px-3 py-1.5 text-[13px] text-paper"
        >
          <RotateCcw className="h-3.5 w-3.5" strokeWidth={1.5} />
          Try again
        </button>
      </div>
    </div>
  );
}
