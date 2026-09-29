// Types mirroring the FastAPI Pydantic models

export interface Evidence {
  decision_id: string;
  summary: string;
  rationale: string;
  confidence: "high" | "medium" | "low";
  source_type: string;
  source_id: number | string | null;
  source_url: string | null;
  evidence_snippet: string | null;
  score: number;
  people: string[];
  dates: string[];
}

export interface GraphNode {
  label: string;
  key: string;
}

export interface ArchitectureStep {
  title: string;
  description: string;
  file_path?: string | null;
  component?: string | null;
}

export interface KeyModule {
  name: string;
  file: string;
  role: string;
  description: string;
}

export interface AskResponse {
  answer: string;
  confidence: "high" | "medium" | "low" | string;
  category?: "historical" | "repository" | "general" | "hybrid";
  overview?: string | null;
  concept?: string | null;
  how_it_works?: string | null;
  in_repository?: string | null;
  architecture_flow?: ArchitectureStep[];
  key_modules?: KeyModule[];
  relevant_files?: string[];
  sources: string[];
  evidence: Evidence[];
  people: string[];
  dates: string[];
  graph_path: GraphNode[];
  mode: string;
}

export interface AskRequest {
  question: string;
  top_k?: number;
}

export interface Decision {
  id: string;
  summary: string;
  rationale: string;
  tradeoffs: string;
  confidence: "high" | "medium" | "low";
  source_type: string;
  source_id: number | string | null;
  source_url: string | null;
  evidence_snippet: string | null;
  people: string[];
  dates: string[];
  golden_id?: number;
}

export interface DecisionsResponse {
  total: number;
  offset: number;
  limit: number;
  decisions: Decision[];
}

export interface HealthResponse {
  status: string;
  neo4j: boolean;
  llm: boolean;
}

export interface StatsResponse {
  decision_count: number;
  golden_question_count: number;
  contributor_count: number;
  confidence_distribution: Record<string, number>;
  source_type_distribution: Record<string, number>;
  neo4j_connected: boolean;
  llm_connected: boolean;
  repo: string;
}

export interface GoldenQuestion {
  id: number;
  question: string;
  confidence: string;
  source_type: string;
}

export interface GoldenQuestionsResponse {
  questions: GoldenQuestion[];
}
