"use client";

import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

interface MemoryRelationship {
  id: string;
  from_memory_id: string;
  to_memory_id: string;
  relationship_type: "related" | "contradicts" | "updates";
  strength: number;
  metadata?: Record<string, any>;
  created_at: string;
}

interface MemoryAnalyticsSummary {
  total_memories_tracked: number;
  total_access_events: number;
  total_search_events: number;
  most_used_memories: Array<{ memory_id: string; count: number }>;
  most_effective_memories: Array<{ memory_id: string; effectiveness_score: number; usage_count: number }>;
  search_frequency: {
    total_searches: number;
    avg_retrieval_count: number;
    avg_usage_count: number;
    avg_effectiveness: number;
    days_analyzed: number;
  };
}

export function AdvancedMemoryPanel() {
  const [selectedMemoryId, setSelectedMemoryId] = useState("");
  const [relationships, setRelationships] = useState<MemoryRelationship[]>([]);
  const [analytics, setAnalytics] = useState<MemoryAnalyticsSummary | null>(null);
  const [expiringSoon, setExpiringSoon] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"relationships" | "expiration" | "analytics">("relationships");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
    loadExpiringSoon();
  }, []);

  useEffect(() => {
    if (selectedMemoryId) {
      loadRelationships();
    }
  }, [selectedMemoryId]);

  const loadRelationships = async () => {
    if (!selectedMemoryId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/memory/${selectedMemoryId}/relationships`);
      if (response.ok) {
        const data = await response.json();
        setRelationships(data.relationships || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load relationships");
    } finally {
      setIsLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE}/memory/analytics/summary`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error("Failed to load analytics:", err);
    }
  };

  const loadExpiringSoon = async () => {
    try {
      const response = await fetch(`${API_BASE}/memory/expiration/expiring-soon?days=7`);
      if (response.ok) {
        const data = await response.json();
        setExpiringSoon(data.expiring_memories || []);
      }
    } catch (err) {
      console.error("Failed to load expiring memories:", err);
    }
  };

  const handleCreateRelationship = async (
    toMemoryId: string,
    relationshipType: "related" | "contradicts" | "updates",
    strength: number = 1.0
  ) => {
    if (!selectedMemoryId) {
      setError("Please select a memory first");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/memory/${selectedMemoryId}/relationships`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_memory_id: toMemoryId,
          relationship_type: relationshipType,
          strength,
        }),
      });
      if (response.ok) {
        await loadRelationships();
      } else {
        throw new Error("Failed to create relationship");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create relationship");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetExpiration = async (memoryId: string, ttlDays?: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/memory/${memoryId}/expiration`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ttl_days: ttlDays, auto_cleanup: true }),
      });
      if (!response.ok) throw new Error("Failed to set expiration");
      await loadExpiringSoon();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to set expiration");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCleanup = async () => {
    if (!confirm("Are you sure you want to cleanup expired memories? This cannot be undone.")) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/memory/expiration/cleanup`, { method: "POST" });
      if (response.ok) {
        const data = await response.json();
        alert(`Cleaned up ${data.cleaned} expired memories`);
        await loadExpiringSoon();
        await loadAnalytics();
      } else {
        throw new Error("Failed to cleanup expired memories");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cleanup expired memories");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white rounded-lg">
      <h2 className="text-2xl font-bold mb-4">Advanced Memory Management</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-gray-700">
        <button
          onClick={() => setActiveTab("relationships")}
          className={`px-4 py-2 ${activeTab === "relationships" ? "border-b-2 border-blue-500" : ""}`}
        >
          Relationships
        </button>
        <button
          onClick={() => setActiveTab("expiration")}
          className={`px-4 py-2 ${activeTab === "expiration" ? "border-b-2 border-blue-500" : ""}`}
        >
          Expiration
        </button>
        <button
          onClick={() => setActiveTab("analytics")}
          className={`px-4 py-2 ${activeTab === "analytics" ? "border-b-2 border-blue-500" : ""}`}
        >
          Analytics
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
          Error: {error}
        </div>
      )}

      {/* Relationships Tab */}
      {activeTab === "relationships" && (
        <div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Memory ID</label>
            <input
              type="text"
              value={selectedMemoryId}
              onChange={(e) => setSelectedMemoryId(e.target.value)}
              placeholder="Enter memory ID to view relationships"
              className="w-full p-2 bg-gray-800 text-white rounded border border-gray-700"
            />
          </div>

          {relationships.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Relationships ({relationships.length})</h3>
              {relationships.map((rel) => (
                <div key={rel.id} className="p-3 bg-gray-800 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-semibold">{rel.relationship_type}</span>
                      <span className="text-sm text-gray-300 ml-2">
                        {rel.from_memory_id === selectedMemoryId ? "→" : "←"} {rel.to_memory_id}
                      </span>
                    </div>
                    <span className="text-sm text-gray-300">Strength: {rel.strength.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Expiration Tab */}
      {activeTab === "expiration" && (
        <div>
          <div className="mb-4 flex gap-2">
            <button
              onClick={handleCleanup}
              disabled={isLoading}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded"
            >
              Cleanup Expired Memories
            </button>
          </div>

          {expiringSoon.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Expiring Soon ({expiringSoon.length})</h3>
              <div className="space-y-2">
                {expiringSoon.map((item) => (
                  <div key={item.memory_id} className="p-3 bg-yellow-900 rounded">
                    <div className="font-semibold">Memory: {item.memory_id}</div>
                    <div className="text-sm text-gray-300">
                      Expires in {item.days_until_expiration} days
                    </div>
                    <div className="text-sm text-gray-300">
                      Expiration: {new Date(item.expiration_date).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === "analytics" && analytics && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-gray-800 rounded">
              <div className="text-sm text-gray-300">Total Memories</div>
              <div className="text-2xl font-bold">{analytics.total_memories_tracked}</div>
            </div>
            <div className="p-4 bg-gray-800 rounded">
              <div className="text-sm text-gray-300">Access Events</div>
              <div className="text-2xl font-bold">{analytics.total_access_events}</div>
            </div>
            <div className="p-4 bg-gray-800 rounded">
              <div className="text-sm text-gray-300">Search Events</div>
              <div className="text-2xl font-bold">{analytics.total_search_events}</div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Most Used Memories</h3>
            <div className="space-y-2">
              {analytics.most_used_memories.slice(0, 5).map((mem) => (
                <div key={mem.memory_id} className="p-3 bg-gray-800 rounded">
                  <div className="font-semibold">{mem.memory_id}</div>
                  <div className="text-sm text-gray-300">Used {mem.count} times</div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Search Frequency</h3>
            <div className="p-4 bg-gray-800 rounded">
              <div className="text-sm text-gray-300">
                Avg Retrieval: {analytics.search_frequency.avg_retrieval_count.toFixed(2)}
              </div>
              <div className="text-sm text-gray-300">
                Avg Usage: {analytics.search_frequency.avg_usage_count.toFixed(2)}
              </div>
              <div className="text-sm text-gray-300">
                Avg Effectiveness: {(analytics.search_frequency.avg_effectiveness * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

