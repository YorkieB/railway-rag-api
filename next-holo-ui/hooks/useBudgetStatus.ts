/**
 * useBudgetStatus Hook
 * 
 * React hook for fetching and managing budget status.
 */

import { useState, useEffect, useCallback } from "react";
import { getBudgetStatus } from "@/lib/api";
import type { BudgetStatus } from "@/types/budget";

interface UseBudgetStatusOptions {
  userId: string;
  autoRefresh?: boolean;
  refreshInterval?: number; // milliseconds
}

export function useBudgetStatus({
  userId,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
}: UseBudgetStatusOptions) {
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBudget = useCallback(async () => {
    if (!userId) {
      setLoading(false);
      return;
    }

    try {
      setError(null);
      const status = await getBudgetStatus(userId);
      setBudget(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load budget status");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchBudget();

    if (autoRefresh) {
      const interval = setInterval(fetchBudget, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchBudget, autoRefresh, refreshInterval]);

  return {
    budget,
    loading,
    error,
    refetch: fetchBudget,
  };
}

