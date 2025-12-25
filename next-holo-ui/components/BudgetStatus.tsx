/**
 * BudgetStatus Component
 * 
 * Displays context usage and daily budget status with progress bars.
 * Shows warnings at 80% utilization and error state at 100%.
 */

import { useState, useEffect } from "react";
import { getBudgetStatus } from "@/lib/api";
import type { BudgetStatus as BudgetStatusType } from "@/types/budget";

interface BudgetStatusProps {
  userId: string;
  className?: string;
}

export function BudgetStatus({ userId, className = "" }: BudgetStatusProps) {
  const [budget, setBudget] = useState<BudgetStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    const fetchBudget = async () => {
      try {
        setLoading(true);
        const status = await getBudgetStatus(userId);
        setBudget(status);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load budget status");
      } finally {
        setLoading(false);
      }
    };

    fetchBudget();
    // Refresh every 30 seconds
    const interval = setInterval(fetchBudget, 30000);
    return () => clearInterval(interval);
  }, [userId]);

  if (loading) {
    return (
      <div className={`p-4 bg-gray-100 rounded-lg ${className}`}>
        <p className="text-sm text-gray-600">Loading budget status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 bg-red-50 rounded-lg ${className}`}>
        <p className="text-sm text-red-600">Error: {error}</p>
      </div>
    );
  }

  if (!budget) {
    return null;
  }

  const ProgressBar = ({
    label,
    used,
    limit,
    utilization,
    unit = "",
  }: {
    label: string;
    used: number;
    limit: number;
    utilization: number;
    unit?: string;
  }) => {
    const isWarning = utilization >= 0.8 && utilization < 1.0;
    const isError = utilization >= 1.0;
    
    const bgColor = isError
      ? "bg-red-500"
      : isWarning
      ? "bg-yellow-500"
      : "bg-blue-500";

    return (
      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm text-gray-600">
            {used.toLocaleString()}{unit} / {limit.toLocaleString()}{unit}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`${bgColor} h-2 rounded-full transition-all duration-300`}
            style={{ width: `${Math.min(utilization * 100, 100)}%` }}
          />
        </div>
        {isWarning && (
          <p className="text-xs text-yellow-600 mt-1">⚠️ Approaching limit</p>
        )}
        {isError && (
          <p className="text-xs text-red-600 mt-1">❌ Limit exceeded</p>
        )}
      </div>
    );
  };

  return (
    <div className={`p-4 bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Budget Status</h3>
      
      <ProgressBar
        label="Text Tokens"
        used={budget.text_tokens.used}
        limit={budget.text_tokens.limit}
        utilization={budget.text_tokens.utilization}
      />
      
      <ProgressBar
        label="Vision Tokens"
        used={budget.vision_tokens.used}
        limit={budget.vision_tokens.limit}
        utilization={budget.vision_tokens.utilization}
      />
      
      <ProgressBar
        label="Audio Minutes"
        used={budget.audio_minutes.used}
        limit={budget.audio_minutes.limit}
        utilization={budget.audio_minutes.utilization}
        unit=" min"
      />
      
      <ProgressBar
        label="Cost"
        used={budget.dollars.used}
        limit={budget.dollars.limit}
        utilization={budget.dollars.utilization}
        unit="$"
      />

      {budget.warnings.length > 0 && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm font-medium text-yellow-800 mb-1">Warnings:</p>
          <ul className="text-xs text-yellow-700 list-disc list-inside">
            {budget.warnings.map((warning, idx) => (
              <li key={idx}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {budget.is_exceeded && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
          <p className="text-sm font-medium text-red-800">
            ⛔ Daily budget limit reached. Please try again tomorrow.
          </p>
        </div>
      )}

      <p className="text-xs text-gray-500 mt-4">
        Resets daily at midnight UTC
      </p>
    </div>
  );
}

