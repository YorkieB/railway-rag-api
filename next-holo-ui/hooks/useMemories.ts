/**
 * useMemories Hook
 * 
 * React hook for fetching and managing memories.
 */

import { useState, useEffect, useCallback } from "react";
import {
  listMemories,
  searchMemories,
  createMemory,
  updateMemory,
  deleteMemory,
} from "@/lib/api";
import type {
  MemoryItem,
  MemoryCreateRequest,
  MemoryUpdateRequest,
} from "@/types/memory";

interface UseMemoriesOptions {
  userId: string;
  projectId?: string | null;
  searchQuery?: string;
  memoryType?: "fact" | "preference" | "decision";
}

export function useMemories({
  userId,
  projectId = null,
  searchQuery = "",
  memoryType,
}: UseMemoriesOptions) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMemories = useCallback(async () => {
    if (!userId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (searchQuery.trim()) {
        const result = await searchMemories({
          user_id: userId,
          query: searchQuery,
          project_id: projectId,
          memory_type: memoryType,
        });
        setMemories(result.memories);
      } else {
        const result = await listMemories(userId, projectId, memoryType);
        setMemories(result.memories);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memories");
    } finally {
      setLoading(false);
    }
  }, [userId, projectId, searchQuery, memoryType]);

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  const create = useCallback(
    async (request: MemoryCreateRequest, privateSession: boolean = false) => {
      try {
        const newMemory = await createMemory(request, privateSession);
        await fetchMemories();
        return newMemory;
      } catch (err) {
        throw new Error(
          err instanceof Error ? err.message : "Failed to create memory"
        );
      }
    },
    [fetchMemories]
  );

  const update = useCallback(
    async (
      memoryId: string,
      updates: MemoryUpdateRequest,
      privateSession: boolean = false
    ) => {
      try {
        await updateMemory(memoryId, userId, updates, privateSession);
        await fetchMemories();
      } catch (err) {
        throw new Error(
          err instanceof Error ? err.message : "Failed to update memory"
        );
      }
    },
    [userId, fetchMemories]
  );

  const remove = useCallback(
    async (memoryId: string, privateSession: boolean = false) => {
      try {
        await deleteMemory(memoryId, userId, privateSession);
        await fetchMemories();
      } catch (err) {
        throw new Error(
          err instanceof Error ? err.message : "Failed to delete memory"
        );
      }
    },
    [userId, fetchMemories]
  );

  return {
    memories,
    loading,
    error,
    refetch: fetchMemories,
    create,
    update,
    delete: remove,
  };
}

