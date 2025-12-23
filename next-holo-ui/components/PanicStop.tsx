"use client";

import { useState, useEffect, useCallback } from "react";
import {
  triggerPanicStop,
  getPanicStatus,
  getAutomationStatus,
  getAutomationConsole,
  type PanicStatus,
  type AutomationStatus,
  type AutomationConsole,
} from "@/lib/api";

export function PanicStop() {
  const [panicStatus, setPanicStatus] = useState<PanicStatus | null>(null);
  const [automationStatus, setAutomationStatus] = useState<AutomationStatus | null>(null);
  const [console, setConsole] = useState<AutomationConsole | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshStatus = useCallback(async () => {
    try {
      const [panic, automation, consoleData] = await Promise.all([
        fetch(`${API_BASE}/windows/panic/status`).then(r => r.json()),
        fetch(`${API_BASE}/windows/automation/status`).then(r => r.json()),
        fetch(`${API_BASE}/windows/automation/console?limit=10`).then(r => r.json()),
      ]);
      setPanicStatus(panic);
      setAutomationStatus(automation);
      setConsole(consoleData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh status");
    }
  }, []);

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 2000); // Refresh every 2 seconds
    return () => clearInterval(interval);
  }, [refreshStatus]);

  const handlePanicStop = useCallback(async () => {
    if (!confirm("Are you sure you want to trigger panic stop? This will immediately cancel all active automations.")) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/windows/panic/stop`, { method: "POST" });
      if (!response.ok) throw new Error(`Failed to trigger panic stop: ${response.statusText}`);
      await refreshStatus();
      alert("Panic stop triggered successfully!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to trigger panic stop");
    } finally {
      setIsLoading(false);
    }
  }, [refreshStatus]);

  const handleKeyboardShortcut = useCallback(
    (e: KeyboardEvent) => {
      // Ctrl+Alt+J for panic stop
      if (e.ctrlKey && e.altKey && e.key === "j") {
        e.preventDefault();
        handlePanicStop();
      }
    },
    [handlePanicStop]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyboardShortcut);
    return () => window.removeEventListener("keydown", handleKeyboardShortcut);
  }, [handleKeyboardShortcut]);

  return (
    <div className="p-6 bg-gray-900 text-white rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Panic Stop & Automation Status</h2>
        <button
          onClick={handlePanicStop}
          disabled={isLoading || !panicStatus?.active_automations.length}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded font-semibold"
        >
          {isLoading ? "Stopping..." : "PANIC STOP (Ctrl+Alt+J)"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
          Error: {error}
        </div>
      )}

      {/* Current Automation Status */}
      {automationStatus && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2">Current Automation</h3>
          {automationStatus.automation ? (
            <div className="bg-gray-800 p-4 rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">{automationStatus.automation.action_description}</span>
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    automationStatus.status === "active"
                      ? "bg-green-600"
                      : automationStatus.status === "paused"
                      ? "bg-yellow-600"
                      : "bg-gray-600"
                  }`}
                >
                  {automationStatus.status.toUpperCase()}
                </span>
              </div>
              <div className="text-sm text-gray-300">
                <div>Step: {automationStatus.automation.current_step} / {automationStatus.automation.total_steps}</div>
                {automationStatus.elapsed_seconds !== null && (
                  <div>Elapsed: {Math.floor(automationStatus.elapsed_seconds)}s</div>
                )}
                {automationStatus.show_banner && (
                  <div className="mt-2 p-2 bg-yellow-900 text-yellow-100 rounded">
                    ⚠️ Long-running automation detected
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 p-4 rounded text-gray-400">No active automation</div>
          )}
        </div>
      )}

      {/* Active Automations */}
      {panicStatus && panicStatus.active_automations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2">Active Automations ({panicStatus.total_active})</h3>
          <div className="space-y-2">
            {panicStatus.active_automations.map((auto) => (
              <div key={auto.automation_id} className="bg-gray-800 p-3 rounded">
                <div className="font-semibold">{auto.action_type}</div>
                <div className="text-sm text-gray-300">Started: {new Date(auto.started_at).toLocaleTimeString()}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Automation Console */}
      {console && (
        <div>
          <h3 className="text-xl font-semibold mb-2">Automation History</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {console.history.length > 0 ? (
              console.history.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded ${
                    item.success ? "bg-gray-800" : "bg-red-900"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold">{item.action_description}</span>
                    <span className="text-sm text-gray-300">
                      {item.duration_seconds.toFixed(1)}s
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">
                    {item.started_at && new Date(item.started_at).toLocaleString()}
                    {item.error && <div className="text-red-300 mt-1">Error: {item.error}</div>}
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-gray-800 p-4 rounded text-gray-400">No automation history</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

