import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function confidenceColor(confidence: string): string {
  switch (confidence) {
    case "high":
      return "text-ink";
    case "medium":
      return "text-graphite";
    case "low":
      return "text-stone";
    default:
      return "text-stone";
  }
}

export function confidenceBg(confidence: string): string {
  switch (confidence) {
    case "high":
      return "text-ember";
    case "medium":
      return "text-graphite";
    case "low":
      return "text-stone";
    default:
      return "text-stone";
  }
}

export function yearFromDate(dateStr?: string): string {
  if (!dateStr) return "Undated";
  const year = new Date(dateStr).getFullYear();
  return Number.isFinite(year) ? String(year) : "Undated";
}

export function sourceTypeIcon(sourceType: string): string {
  switch (sourceType) {
    case "github_pr":
      return "GitPullRequest";
    case "github_issue":
      return "CircleDot";
    case "github_commit":
      return "GitCommitHorizontal";
    default:
      return "FileQuestion";
  }
}

export function sourceTypeLabel(sourceType: string): string {
  switch (sourceType) {
    case "github_pr":
      return "Pull Request";
    case "github_issue":
      return "Issue";
    case "github_commit":
      return "Commit";
    default:
      return "Unknown";
  }
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "…";
}
