/**
 * Budget API Client Functions
 * 
 * Centralized API calls for budget and cost operations.
 */

import type { BudgetStatus } from "@/types/budget";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

/**
 * Get current budget status for a user.
 */
export async function getBudgetStatus(userId: string): Promise<BudgetStatus> {
  const response = await fetch(`${API_BASE}/budget/status?user_id=${userId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || error.message || "Failed to get budget status");
  }

  return response.json();
}

