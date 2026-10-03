import type {
  AskRequest,
  AskResponse,
  Decision,
  DecisionsResponse,
  GoldenQuestionsResponse,
  HealthResponse,
  StatsResponse,
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

class APIError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API Error ${status}: ${detail}`);
    this.status = status;
    this.detail = detail;
  }
}

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse errors
    }
    throw new APIError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

// ─── Health & Stats ──────────────────────────────────────────────

export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

export async function getStats(): Promise<StatsResponse> {
  return apiFetch<StatsResponse>("/stats");
}

// ─── Investigation ───────────────────────────────────────────────

export async function askQuestion(
  request: AskRequest
): Promise<AskResponse> {
  return apiFetch<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

// ─── Decisions ───────────────────────────────────────────────────

export async function getDecisions(params?: {
  confidence?: string;
  source_type?: string;
  limit?: number;
  offset?: number;
}): Promise<DecisionsResponse> {
  const searchParams = new URLSearchParams();
  if (params?.confidence) searchParams.set("confidence", params.confidence);
  if (params?.source_type) searchParams.set("source_type", params.source_type);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  return apiFetch<DecisionsResponse>(
    `/decisions${query ? `?${query}` : ""}`
  );
}

export async function getDecision(id: string): Promise<Decision> {
  return apiFetch<Decision>(`/decision/${encodeURIComponent(id)}`);
}

// ─── Golden Questions ────────────────────────────────────────────

export async function getGoldenQuestions(): Promise<GoldenQuestionsResponse> {
  return apiFetch<GoldenQuestionsResponse>("/golden-questions");
}

// ─── Conversational AI (Sarvam AI) ──────────────────────────────

export async function sendChatMessage(
  request: import("@/types/api").ChatRequest
): Promise<import("@/types/api").ChatResponse> {
  return apiFetch<import("@/types/api").ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getChatSession(
  sessionId: string
): Promise<import("@/types/api").ChatSessionInfo> {
  return apiFetch<import("@/types/api").ChatSessionInfo>(
    `/chat/session/${encodeURIComponent(sessionId)}`
  );
}

export async function clearChatSession(
  sessionId: string
): Promise<{ status: string; session_id: string; cleared: boolean }> {
  return apiFetch<{ status: string; session_id: string; cleared: boolean }>(
    `/chat/session/${encodeURIComponent(sessionId)}`,
    {
      method: "DELETE",
    }
  );
}

// ─── Export error class for consumers ────────────────────────────

export { APIError };
