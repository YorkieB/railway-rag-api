import React from "react";

export interface BudgetStatusProps {
  tokens?: number;
  tokensLimit?: number;
  dollars?: number;
  dollarsLimit?: number;
  utilization?: number;
  warning?: boolean;
}

export function BudgetStatus({
  tokens = 0,
  tokensLimit = 500000,
  dollars = 0,
  dollarsLimit = 10.0,
  utilization = 0,
  warning = false
}: BudgetStatusProps) {
  const tokensUtilization = tokensLimit > 0 ? (tokens / tokensLimit) * 100 : 0;
  const dollarsUtilization = dollarsLimit > 0 ? (dollars / dollarsLimit) * 100 : 0;
  const maxUtilization = Math.max(tokensUtilization, dollarsUtilization);

  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">Daily Budget Status</h3>
      
      {/* Tokens Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Tokens</span>
          <span>
            {tokens.toLocaleString()} / {tokensLimit.toLocaleString()}
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              tokensUtilization >= 100
                ? "bg-red-500"
                : tokensUtilization >= 80
                ? "bg-yellow-500"
                : "bg-green-500"
            }`}
            style={{ width: `${Math.min(tokensUtilization, 100)}%` }}
          />
        </div>
      </div>

      {/* Dollars Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Cost</span>
          <span>
            ${dollars.toFixed(2)} / ${dollarsLimit.toFixed(2)}
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              dollarsUtilization >= 100
                ? "bg-red-500"
                : dollarsUtilization >= 80
                ? "bg-yellow-500"
                : "bg-green-500"
            }`}
            style={{ width: `${Math.min(dollarsUtilization, 100)}%` }}
          />
        </div>
      </div>

      {/* Warning Message */}
      {warning && (
        <div className="mt-3 p-2 bg-yellow-900/30 border border-yellow-700 rounded text-xs text-yellow-300">
          ⚠️ Approaching daily limit ({maxUtilization.toFixed(1)}% used)
        </div>
      )}

      {maxUtilization >= 100 && (
        <div className="mt-3 p-2 bg-red-900/30 border border-red-700 rounded text-xs text-red-300">
          ❌ Daily limit reached. Requests will be rejected.
        </div>
      )}
    </div>
  );
}

