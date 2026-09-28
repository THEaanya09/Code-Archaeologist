import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen p-6 bg-grid">
      <div className="max-w-md">
        <p className="font-mono text-[13px] text-ember mb-3">404</p>
        <h2 className="text-[17px] font-medium text-ink mb-2">Page not found</h2>
        <p className="text-[14px] text-stone mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-[13px] text-ink border-b border-ink pb-0.5 hover:border-ember hover:text-ember"
        >
          <ArrowLeft className="h-3.5 w-3.5" strokeWidth={1.5} />
          Back to repository
        </Link>
      </div>
    </div>
  );
}
