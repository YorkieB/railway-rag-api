/**
 * Memory API Client Functions
 * 
 * Centralized API calls for memory operations.
 */

import type {
  MemoryItem,
  MemoryCreateRequest,
  MemoryUpdateRequest,
  MemorySearchRequest,
  MemoryListResponse,
  MemorySearchResponse,
} from "@/types/memory";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

/**
 * Create a new memory.
 */
export async function createMemory(
  request: MemoryCreateRequest,
  privateSession: boolean = false
): Promise<MemoryItem> {
  const response = await fetch(`${API_BASE}/memory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...request,
      private_session: privateSession,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to create memory");
  }

  return response.json();
}

/**
 * List memories for a user.
 */
export async function listMemories(
  userId: string,
  projectId?: string | null,
  memoryType?: "fact" | "preference" | "decision",
  limit: number = 100
): Promise<MemoryListResponse> {
  const params = new URLSearchParams({
    user_id: userId,
    limit: limit.toString(),
  });

  if (projectId) {
    params.append("project_id", projectId);
  }
  if (memoryType) {
    params.append("memory_type", memoryType);
  }

  const response = await fetch(`${API_BASE}/memory?${params.toString()}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to list memories");
  }

  return response.json();
}

/**
 * Get a specific memory by ID.
 */
export async function getMemory(
  memoryId: string,
  userId: string
): Promise<MemoryItem> {
  const response = await fetch(
    `${API_BASE}/memory/${memoryId}?user_id=${userId}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to get memory");
  }

  return response.json();
}

/**
 * Update a memory.
 */
export async function updateMemory(
  memoryId: string,
  userId: string,
  updates: MemoryUpdateRequest,
  privateSession: boolean = false
): Promise<MemoryItem> {
  const response = await fetch(`${API_BASE}/memory/${memoryId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...updates,
      user_id: userId,
      private_session: privateSession,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to update memory");
  }

  return response.json();
}

/**
 * Delete a memory.
 */
export async function deleteMemory(
  memoryId: string,
  userId: string,
  privateSession: boolean = false
): Promise<void> {
  const params = new URLSearchParams({
    user_id: userId,
    private_session: privateSession.toString(),
  });

  const response = await fetch(
    `${API_BASE}/memory/${memoryId}?${params.toString()}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to delete memory");
  }
}

/**
 * Search memories using semantic search.
 */
export async function searchMemories(
  request: MemorySearchRequest
): Promise<MemorySearchResponse> {
  const response = await fetch(`${API_BASE}/memory/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to search memories");
  }

  return response.json();
}

