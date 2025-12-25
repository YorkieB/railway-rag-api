/**
 * Memory Types
 */

export interface MemoryItem {
  id: string;
  user_id: string;
  project_id: string | null;
  content: string;
  memory_type: "fact" | "preference" | "decision";
  created_at: string;
  updated_at: string;
}

export interface MemoryCreateRequest {
  user_id: string;
  project_id?: string | null;
  content: string;
  memory_type?: "fact" | "preference" | "decision";
}

export interface MemoryUpdateRequest {
  content?: string;
  memory_type?: "fact" | "preference" | "decision";
  project_id?: string | null;
}

export interface MemorySearchRequest {
  user_id: string;
  query: string;
  project_id?: string | null;
  memory_type?: "fact" | "preference" | "decision";
  limit?: number;
}

export interface MemoryListResponse {
  memories: MemoryItem[];
  total: number;
}

export interface MemorySearchResponse {
  memories: MemoryItem[];
  query: string;
  total: number;
}

