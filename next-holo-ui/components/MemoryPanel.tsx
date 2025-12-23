import React, { useState, useEffect } from "react";
import { 
  MemoryItem, 
  createMemory, 
  listMemories, 
  searchMemories, 
  updateMemory, 
  deleteMemory 
} from "@/lib/api";

export interface MemoryPanelProps {
  apiBase: string;
  userId: string;
  projectId?: string;
}

export function MemoryPanel({ apiBase, userId, projectId }: MemoryPanelProps) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newMemory, setNewMemory] = useState({
    content: "",
    memory_type: "fact" as "fact" | "preference" | "decision"
  });

  const loadMemories = async () => {
    setLoading(true);
    try {
      const result = await listMemories(apiBase, userId, projectId);
      setMemories(result.memories);
    } catch (err: any) {
      console.error("Failed to load memories:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadMemories();
      return;
    }
    setLoading(true);
    try {
      const result = await searchMemories(apiBase, userId, searchQuery, projectId);
      setMemories(result.memories);
    } catch (err: any) {
      console.error("Failed to search memories:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newMemory.content.trim()) return;
    setLoading(true);
    try {
      await createMemory(apiBase, userId, newMemory.content, newMemory.memory_type, projectId);
      setNewMemory({ content: "", memory_type: "fact" });
      setShowCreate(false);
      await loadMemories();
    } catch (err: any) {
      console.error("Failed to create memory:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (memoryId: string) => {
    if (!confirm("Delete this memory?")) return;
    setLoading(true);
    try {
      await deleteMemory(apiBase, memoryId, userId);
      await loadMemories();
    } catch (err: any) {
      console.error("Failed to delete memory:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [apiBase, userId, projectId]);

  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-200">Memories</h3>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-3 py-1 text-sm bg-purple-600 hover:bg-purple-700 rounded text-white"
        >
          {showCreate ? "Cancel" : "+ New"}
        </button>
      </div>

      {/* Search */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Search memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 text-sm"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
        >
          Search
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="mb-4 p-3 bg-gray-700 rounded border border-gray-600">
          <textarea
            placeholder="Memory content..."
            value={newMemory.content}
            onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-200 text-sm mb-2"
            rows={3}
          />
          <select
            value={newMemory.memory_type}
            onChange={(e) => setNewMemory({ ...newMemory, memory_type: e.target.value as any })}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-200 text-sm mb-2"
          >
            <option value="fact">Fact</option>
            <option value="preference">Preference</option>
            <option value="decision">Decision</option>
          </select>
          <button
            onClick={handleCreate}
            disabled={loading || !newMemory.content.trim()}
            className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-white text-sm"
          >
            Create Memory
          </button>
        </div>
      )}

      {/* Memory List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {loading && <div className="text-gray-400 text-sm">Loading...</div>}
        {!loading && memories.length === 0 && (
          <div className="text-gray-400 text-sm">No memories found</div>
        )}
        {memories.map((memory) => (
          <div
            key={memory.id}
            className="p-3 bg-gray-700 rounded border border-gray-600"
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`text-xs px-2 py-1 rounded ${
                memory.memory_type === "fact" ? "bg-blue-900 text-blue-200" :
                memory.memory_type === "preference" ? "bg-purple-900 text-purple-200" :
                "bg-green-900 text-green-200"
              }`}>
                {memory.memory_type}
              </span>
              <button
                onClick={() => handleDelete(memory.id)}
                className="text-red-400 hover:text-red-300 text-xs"
              >
                Delete
              </button>
            </div>
            <div className="text-gray-200 text-sm">{memory.content}</div>
            {memory.project_id && (
              <div className="text-xs text-gray-400 mt-1">Project: {memory.project_id}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

