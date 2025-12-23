"use client";

import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

interface TestResult {
  id: string;
  question: string;
  score: number;
  status: "passed" | "failed" | "skipped";
  answer?: string;
  sources?: any[];
  uncertain?: boolean;
  error?: string;
}

interface RegressionReport {
  baseline_found: boolean;
  baseline_name?: string;
  baseline_date?: string;
  comparison_date?: string;
  regressions?: Array<{
    test_id: string;
    baseline_score: number;
    current_score: number;
    degradation: number;
  }>;
  improvements?: Array<{
    test_id: string;
    baseline_score: number;
    current_score: number;
    improvement: number;
  }>;
  unchanged?: string[];
  total_regressions?: number;
  total_improvements?: number;
  regression_detected?: boolean;
  baseline_summary?: {
    total: number;
    average_score: number;
    passed: number;
    failed: number;
    pass_rate: number;
  };
  current_summary?: {
    total: number;
    average_score: number;
    passed: number;
    failed: number;
    pass_rate: number;
  };
  alerts?: Array<{
    level: string;
    message: string;
  }>;
}

export function EvaluationDashboard() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [regressionReport, setRegressionReport] = useState<RegressionReport | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"results" | "regression" | "run">("results");

  useEffect(() => {
    loadRegressionReport();
  }, []);

  const loadRegressionReport = async () => {
    try {
      // In a real implementation, this would fetch from an API endpoint
      // For now, we'll use a placeholder
      setIsLoading(true);
      // Mock data for demonstration
      setRegressionReport(null);
    } catch (err) {
      console.error("Failed to load regression report:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const runTests = async () => {
    setIsRunning(true);
    setError(null);
    try {
      // In a real implementation, this would call an API endpoint to run tests
      // For now, we'll use a placeholder
      await new Promise((resolve) => setTimeout(resolve, 2000)); // Simulate test run
      alert("Tests completed! (This is a placeholder - implement API endpoint)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run tests");
    } finally {
      setIsRunning(false);
    }
  };

  const createBaseline = async () => {
    if (!confirm("Create baseline from current test results?")) {
      return;
    }

    try {
      // In a real implementation, this would call an API endpoint
      alert("Baseline created! (This is a placeholder - implement API endpoint)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create baseline");
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white rounded-lg">
      <h2 className="text-2xl font-bold mb-4">Evaluation Dashboard</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-gray-700">
        <button
          onClick={() => setActiveTab("results")}
          className={`px-4 py-2 ${activeTab === "results" ? "border-b-2 border-blue-500" : ""}`}
        >
          Test Results
        </button>
        <button
          onClick={() => setActiveTab("regression")}
          className={`px-4 py-2 ${activeTab === "regression" ? "border-b-2 border-blue-500" : ""}`}
        >
          Regression
        </button>
        <button
          onClick={() => setActiveTab("run")}
          className={`px-4 py-2 ${activeTab === "run" ? "border-b-2 border-blue-500" : ""}`}
        >
          Run Tests
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
          Error: {error}
        </div>
      )}

      {/* Test Results Tab */}
      {activeTab === "results" && (
        <div>
          {testResults.length > 0 ? (
            <div className="space-y-2">
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="p-4 bg-gray-800 rounded">
                  <div className="text-sm text-gray-300">Total Tests</div>
                  <div className="text-2xl font-bold">{testResults.length}</div>
                </div>
                <div className="p-4 bg-gray-800 rounded">
                  <div className="text-sm text-gray-300">Passed</div>
                  <div className="text-2xl font-bold text-green-400">
                    {testResults.filter((r) => r.status === "passed").length}
                  </div>
                </div>
                <div className="p-4 bg-gray-800 rounded">
                  <div className="text-sm text-gray-300">Failed</div>
                  <div className="text-2xl font-bold text-red-400">
                    {testResults.filter((r) => r.status === "failed").length}
                  </div>
                </div>
                <div className="p-4 bg-gray-800 rounded">
                  <div className="text-sm text-gray-300">Avg Score</div>
                  <div className="text-2xl font-bold">
                    {testResults.length > 0
                      ? (testResults.reduce((sum, r) => sum + r.score, 0) / testResults.length).toFixed(1)
                      : "0.0"}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                {testResults.map((result) => (
                  <div
                    key={result.id}
                    className={`p-3 rounded ${
                      result.status === "passed" ? "bg-green-900" : result.status === "failed" ? "bg-red-900" : "bg-gray-800"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">{result.id}</span>
                      <span className="text-sm">Score: {result.score}/10</span>
                    </div>
                    <div className="text-sm text-gray-300">{result.question}</div>
                    {result.error && <div className="text-sm text-red-300 mt-1">Error: {result.error}</div>}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 p-4 rounded text-gray-400">No test results available. Run tests first.</div>
          )}
        </div>
      )}

      {/* Regression Tab */}
      {activeTab === "regression" && (
        <div>
          <div className="mb-4 flex gap-2">
            <button
              onClick={createBaseline}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
            >
              Create Baseline
            </button>
          </div>

          {regressionReport ? (
            <div className="space-y-4">
              {regressionReport.regression_detected && (
                <div className="p-4 bg-red-900 rounded">
                  <div className="font-semibold text-red-100">⚠️ Regression Detected</div>
                  <div className="text-sm text-red-200 mt-1">
                    {regressionReport.total_regressions} tests degraded
                  </div>
                </div>
              )}

              {regressionReport.regressions && regressionReport.regressions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Regressions ({regressionReport.regressions.length})</h3>
                  <div className="space-y-2">
                    {regressionReport.regressions.map((reg) => (
                      <div key={reg.test_id} className="p-3 bg-red-900 rounded">
                        <div className="font-semibold">{reg.test_id}</div>
                        <div className="text-sm text-gray-300">
                          Score: {reg.baseline_score} → {reg.current_score} (degradation: {reg.degradation})
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {regressionReport.improvements && regressionReport.improvements.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Improvements ({regressionReport.improvements.length})</h3>
                  <div className="space-y-2">
                    {regressionReport.improvements.map((imp) => (
                      <div key={imp.test_id} className="p-3 bg-green-900 rounded">
                        <div className="font-semibold">{imp.test_id}</div>
                        <div className="text-sm text-gray-300">
                          Score: {imp.baseline_score} → {imp.current_score} (improvement: +{imp.improvement})
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {regressionReport.baseline_summary && regressionReport.current_summary && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-800 rounded">
                    <h4 className="font-semibold mb-2">Baseline</h4>
                    <div className="text-sm text-gray-300">
                      <div>Total: {regressionReport.baseline_summary.total}</div>
                      <div>Avg Score: {regressionReport.baseline_summary.average_score.toFixed(2)}</div>
                      <div>Pass Rate: {regressionReport.baseline_summary.pass_rate.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-800 rounded">
                    <h4 className="font-semibold mb-2">Current</h4>
                    <div className="text-sm text-gray-300">
                      <div>Total: {regressionReport.current_summary.total}</div>
                      <div>Avg Score: {regressionReport.current_summary.average_score.toFixed(2)}</div>
                      <div>Pass Rate: {regressionReport.current_summary.pass_rate.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-800 p-4 rounded text-gray-400">
              No regression report available. Run regression tests first.
            </div>
          )}
        </div>
      )}

      {/* Run Tests Tab */}
      {activeTab === "run" && (
        <div>
          <div className="mb-4">
            <button
              onClick={runTests}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-semibold"
            >
              {isRunning ? "Running Tests..." : "Run Evaluation Suite"}
            </button>
          </div>

          <div className="bg-gray-800 p-4 rounded">
            <h3 className="font-semibold mb-2">Test Categories</h3>
            <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
              <li>RAG Success Tests (10 tests)</li>
              <li>Empty Retrieval Tests (8 tests)</li>
              <li>Memory Recall Tests (7 tests)</li>
              <li>V1 Browser Automation Tests (5 tests)</li>
              <li>V1 Screen Share Tests (4 tests)</li>
              <li>V2 Windows Companion Tests (5 tests)</li>
              <li>V2 Multi-Agent Tests (3 tests)</li>
              <li>V2 Advanced Memory Tests (4 tests)</li>
              <li>And more...</li>
            </ul>
            <div className="mt-4 text-sm text-gray-400">
              Total: ~80+ test cases covering all V1 and V2 features
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

