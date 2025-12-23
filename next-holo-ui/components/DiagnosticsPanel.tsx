"use client";

import { useState, useEffect, useMemo } from "react";
import { diagnostics, type DiagnosticLog, type LogLevel } from "@/lib/diagnostics";

type Props = {
  apiBase: string;
};

export function DiagnosticsPanel({ apiBase }: Props) {
  const [logs, setLogs] = useState<DiagnosticLog[]>([]);
  const [filter, setFilter] = useState<{ level?: LogLevel; category?: string }>({});
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    // Initial load
    setLogs(diagnostics.getLogs(100));

    // Subscribe to new logs
    const unsubscribe = diagnostics.subscribe((log) => {
      if (log.id !== "clear") {
        setLogs(prev => [log, ...prev].slice(0, 100));
      } else {
        setLogs([]);
      }
    });

    // Auto-refresh
    let interval: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      interval = setInterval(() => {
        setLogs(diagnostics.getLogs(100));
      }, 1000);
    }

    return () => {
      unsubscribe();
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filter.level && log.level !== filter.level) return false;
      if (filter.category && log.category !== filter.category) return false;
      return true;
    });
  }, [logs, filter]);

  const errorCount = logs.filter(l => l.level === "error").length;
  const warningCount = logs.filter(l => l.level === "warning").length;

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getLevelColor = (level: LogLevel) => {
    switch (level) {
      case "error": return "text-red-600 bg-red-50 border-red-200";
      case "warning": return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "success": return "text-green-600 bg-green-50 border-green-200";
      case "info": return "text-blue-600 bg-blue-50 border-blue-200";
    }
  };

  const getLevelIcon = (level: LogLevel) => {
    switch (level) {
      case "error": return "❌";
      case "warning": return "⚠️";
      case "success": return "✅";
      case "info": return "ℹ️";
    }
  };

  const runHealthChecks = async () => {
    diagnostics.info("system", "Running health checks...");
    
    // Check rag-api
    try {
      const response = await fetch(`${apiBase}/health`);
      if (response.ok) {
        const data = await response.json();
        diagnostics.logHealthCheck("rag-api", "ok", data);
      } else {
        diagnostics.logHealthCheck("rag-api", "failed", { status: response.status });
      }
    } catch (error) {
      diagnostics.logConnectionError("rag-api", error, apiBase);
    }

    // Check companion-api
    const companionApiBase = apiBase.replace("api.", "companion.").replace(":8080", ":8081");
    try {
      const response = await fetch(`${companionApiBase}/health`);
      if (response.ok) {
        const data = await response.json();
        diagnostics.logHealthCheck("companion-api", "ok", data);
      } else {
        diagnostics.logHealthCheck("companion-api", "failed", { status: response.status });
      }
    } catch (error) {
      diagnostics.logConnectionError("companion-api", error, companionApiBase);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Diagnostics</h3>
          <p className="text-xs text-gray-600 mt-1">
            System logs and error tracking
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={runHealthChecks}
            className="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
          >
            Run Health Checks
          </button>
          <button
            onClick={() => diagnostics.clear()}
            className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Clear Logs
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <div className="text-xs text-red-600 font-medium">Errors</div>
          <div className="text-lg font-bold text-red-700">{errorCount}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
          <div className="text-xs text-yellow-600 font-medium">Warnings</div>
          <div className="text-lg font-bold text-yellow-700">{warningCount}</div>
        </div>
        <div className="bg-gray-50 border border-gray-200 rounded p-2">
          <div className="text-xs text-gray-600 font-medium">Total Logs</div>
          <div className="text-lg font-bold text-gray-700">{logs.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        <select
          value={filter.level || ""}
          onChange={(e) => setFilter(prev => ({ ...prev, level: e.target.value as LogLevel || undefined }))}
          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white"
        >
          <option value="">All Levels</option>
          <option value="error">Errors</option>
          <option value="warning">Warnings</option>
          <option value="info">Info</option>
          <option value="success">Success</option>
        </select>
        <select
          value={filter.category || ""}
          onChange={(e) => setFilter(prev => ({ ...prev, category: e.target.value || undefined }))}
          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white"
        >
          <option value="">All Categories</option>
          <option value="api">API</option>
          <option value="connection">Connection</option>
          <option value="websocket">WebSocket</option>
          <option value="health">Health</option>
          <option value="configuration">Configuration</option>
          <option value="unhandled">Unhandled</option>
          <option value="system">System</option>
        </select>
        <label className="flex items-center gap-1 text-xs text-gray-600">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="rounded"
          />
          Auto-refresh
        </label>
      </div>

      {/* Logs */}
      <div className="border border-gray-200 rounded-lg bg-gray-50 max-h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            No logs found. {logs.length === 0 ? "Logs will appear here when issues occur." : "Try adjusting filters."}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredLogs.map((log) => (
              <div
                key={log.id}
                className={`p-3 border-l-4 ${getLevelColor(log.level)}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm">{getLevelIcon(log.level)}</span>
                      <span className="text-xs font-medium uppercase">{log.category}</span>
                      <span className="text-xs text-gray-500">{formatTime(log.timestamp)}</span>
                    </div>
                    <div className="text-sm font-medium break-words">{log.message}</div>
                    {log.details && (
                      <details className="mt-1">
                        <summary className="text-xs text-gray-600 cursor-pointer">Details</summary>
                        <pre className="text-xs mt-1 p-2 bg-gray-100 rounded overflow-x-auto">
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      </details>
                    )}
                    {log.stack && (
                      <details className="mt-1">
                        <summary className="text-xs text-gray-600 cursor-pointer">Stack Trace</summary>
                        <pre className="text-xs mt-1 p-2 bg-gray-100 rounded overflow-x-auto">
                          {log.stack}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

