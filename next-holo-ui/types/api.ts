/**
 * API Response Types
 * 
 * Types for API responses including uncertainty and memory-enhanced responses.
 */

export interface RAGSource {
  document_name: string;
  chunk_index: number;
  text: string;
  score: number;
}

export interface MemoryUsed {
  id: string;
  content: string;
  type: "fact" | "preference" | "decision";
}

export interface RAGResponse {
  answer: string;
  sources: RAGSource[];
  uncertain: boolean;
  suggestions?: string[];
  memories_used?: MemoryUsed[];
  warning?: string;
  cost?: {
    tokens: number;
    dollars: number;
  };
}

export interface UncertainResponse {
  answer: string;
  uncertain: true;
  suggestions: string[];
  reason: string;
}

export interface BudgetExceededResponse {
  error: string;
  message: string;
  code: "BUDGET_EXCEEDED";
  budget_status: any;
}

