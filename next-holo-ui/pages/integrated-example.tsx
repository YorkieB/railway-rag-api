/**
 * Integrated Page Example
 * 
 * This file shows how to integrate ALL Sprint 1.3 and 2.4 components
 * into a Next.js page.
 * 
 * IMPORTANT: This is an EXAMPLE file. Use this as a reference for integrating
 * into your actual pages/index.tsx or other pages.
 */

import React, { useState } from "react";
import { BudgetStatus } from "@/components/BudgetStatus";
import { MemoryPanel } from "@/components/MemoryPanel";
import { UncertaintyBanner } from "@/components/UncertaintyBanner";
import { BrowserPanel } from "@/components/BrowserPanel";

export default function IntegratedExamplePage() {
  // Example user ID - replace with actual authentication
  const [userId] = useState("user123");
  const [projectId, setProjectId] = useState<string | undefined>(undefined);
  const [uncertainResponse, setUncertainResponse] = useState<any>(null);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900">Jarvis Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Complete integration of all features: Budget, Memory, Live Sessions, and Browser Automation
          </p>
        </header>

        {/* Budget Status Section */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Budget Status</h2>
          <BudgetStatus userId={userId} />
        </section>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Memory Panel */}
          <section className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Memory Management</h2>
            <MemoryPanel userId={userId} projectId={projectId} />
          </section>

          {/* Browser Panel */}
          <section className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Browser Automation</h2>
            <BrowserPanel userId={userId} />
          </section>
        </div>

        {/* Uncertainty Banner */}
        {uncertainResponse && (
          <section className="bg-white rounded-lg shadow p-6">
            <UncertaintyBanner response={uncertainResponse} />
          </section>
        )}

        {/* Example: Chat Interface Integration */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Chat Interface</h2>
          <div className="space-y-4">
            <textarea
              className="w-full p-3 border rounded-lg"
              placeholder="Enter your query..."
              rows={4}
            />
            <button
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              onClick={async () => {
                // Example query - replace with actual API call
                try {
                  const response = await fetch("/api/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      message: "Example query",
                      user_id: userId,
                      project_id: projectId,
                    }),
                  });
                  
                  const data = await response.json();
                  
                  // Check for uncertainty
                  if (data.uncertain) {
                    setUncertainResponse(data);
                  }
                } catch (error) {
                  console.error("Query failed:", error);
                }
              }}
            >
              Send Query
            </button>
          </div>
        </section>

        {/* Project Selector */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Project Selection</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={projectId || ""}
              onChange={(e) => setProjectId(e.target.value || undefined)}
              placeholder="Enter project ID (optional)"
              className="flex-1 px-3 py-2 border rounded-lg"
            />
            <button
              onClick={() => setProjectId(undefined)}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              Clear
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Project ID: {projectId || "None (global memory)"}
          </p>
        </section>
      </div>
    </div>
  );
}

