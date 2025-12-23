"use client";

import { useState, useEffect } from "react";
import { executeAgentTask, getAgentsStatus, type AgentTaskResponse, type AgentsStatus } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

export function AgentOrchestration() {
  const [taskDescription, setTaskDescription] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<AgentTaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [agentsStatus, setAgentsStatus] = useState<AgentsStatus | null>(null);

  useEffect(() => {
    // Load agents status on mount
    loadAgentsStatus();
  }, []);

  const loadAgentsStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/agents/status`);
      if (response.ok) {
        const status = await response.json();
        setAgentsStatus(status);
      }
    } catch (err) {
      console.error("Failed to load agents status:", err);
    }
  };

  const handleExecute = async () => {
    if (!taskDescription.trim()) {
      setError("Please enter a task description");
      return;
    }

    setIsExecuting(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/agents/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_description: taskDescription,
          user_id: "default",
        }),
      });
      if (!response.ok) throw new Error(`Failed to execute task: ${response.statusText}`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to execute task");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white rounded-lg">
      <h2 className="text-2xl font-bold mb-4">Multi-Agent Task Orchestration</h2>

      {/* Agents Status */}
      {agentsStatus && (
        <div className="mb-6 p-4 bg-gray-800 rounded">
          <h3 className="text-lg font-semibold mb-2">Agents Status</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className={agentsStatus.browser_agent ? "text-green-400" : "text-red-400"}>
              Browser Agent: {agentsStatus.browser_agent ? "✓ Available" : "✗ Unavailable"}
            </div>
            <div className={agentsStatus.os_agent ? "text-green-400" : "text-red-400"}>
              OS Agent: {agentsStatus.os_agent ? "✓ Available" : "✗ Unavailable"}
            </div>
            <div className={agentsStatus.rag_agent ? "text-green-400" : "text-red-400"}>
              RAG Agent: {agentsStatus.rag_agent ? "✓ Available" : "✗ Unavailable"}
            </div>
            <div className={agentsStatus.crewai_available ? "text-green-400" : "text-yellow-400"}>
              CrewAI: {agentsStatus.crewai_available ? "✓ Active" : "⚠ Fallback Mode"}
            </div>
          </div>
        </div>
      )}

      {/* Task Input */}
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-2">Task Description</label>
        <textarea
          value={taskDescription}
          onChange={(e) => setTaskDescription(e.target.value)}
          placeholder="Describe the task you want the agents to perform..."
          className="w-full p-3 bg-gray-800 text-white rounded border border-gray-700 focus:border-blue-500 focus:outline-none"
          rows={4}
          disabled={isExecuting}
        />
      </div>

      <button
        onClick={handleExecute}
        disabled={isExecuting || !taskDescription.trim()}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded font-semibold mb-4"
      >
        {isExecuting ? "Executing..." : "Execute Task"}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
          Error: {error}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-4">
          <div className="p-4 bg-gray-800 rounded">
            <h3 className="text-lg font-semibold mb-2">
              Task {result.success ? "Completed" : "Failed"}
            </h3>
            {result.automation_id && (
              <div className="text-sm text-gray-300 mb-2">
                Automation ID: {result.automation_id}
              </div>
            )}
            {result.total_steps && (
              <div className="text-sm text-gray-300 mb-2">
                Steps: {result.completed_steps} / {result.total_steps}
              </div>
            )}
          </div>

          {/* Plan Display */}
          {result.plan && (
            <div className="p-4 bg-gray-800 rounded">
              <h3 className="text-lg font-semibold mb-2">Execution Plan</h3>
              <div className="space-y-2">
                {result.plan.steps.map((step, idx) => (
                  <div key={idx} className="p-2 bg-gray-700 rounded text-sm">
                    <div className="font-semibold">
                      Step {idx + 1}: {step.agent.toUpperCase()} Agent
                    </div>
                    <div className="text-gray-300">{step.description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step Results */}
          {result.results && result.results.length > 0 && (
            <div className="p-4 bg-gray-800 rounded">
              <h3 className="text-lg font-semibold mb-2">Step Results</h3>
              <div className="space-y-2">
                {result.results.map((stepResult, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded ${
                      stepResult.success ? "bg-green-900" : "bg-red-900"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">
                        Step {idx + 1}: {stepResult.agent.toUpperCase()} Agent
                      </span>
                      <span className={stepResult.success ? "text-green-300" : "text-red-300"}>
                        {stepResult.success ? "✓ Success" : "✗ Failed"}
                      </span>
                    </div>
                    {stepResult.error && (
                      <div className="text-sm text-red-300 mt-1">Error: {stepResult.error}</div>
                    )}
                    {stepResult.result && (
                      <div className="text-sm text-gray-300 mt-1">
                        {JSON.stringify(stepResult.result, null, 2)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

