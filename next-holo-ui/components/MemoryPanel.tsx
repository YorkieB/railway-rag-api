/**
 * MemoryPanel Component
 * 
 * UI for managing memories: list, search, create, edit, delete.
 * Supports global and project-scoped memories.
 * Respects private session mode (no writes).
 */

import { useState, useEffect, useCallback } from "react";
import {
  listMemories,
  searchMemories,
  createMemory,
  updateMemory,
  deleteMemory,
} from "@/lib/api";
import type {
  MemoryItem,
  MemoryCreateRequest,
  MemoryUpdateRequest,
} from "@/types/memory";

interface MemoryPanelProps {
  userId: string;
  projectId?: string | null;
  privateSession?: boolean;
  className?: string;
}

export function MemoryPanel({
  userId,
  projectId = null,
  privateSession = false,
  className = "",
}: MemoryPanelProps) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Form state
  const [formContent, setFormContent] = useState("");
  const [formType, setFormType] = useState<"fact" | "preference" | "decision">("fact");
  const [formProjectId, setFormProjectId] = useState<string | null>(projectId);

  const loadMemories = useCallback(async () => {
    if (!userId) return;

    try {
      setLoading(true);
      setError(null);

      if (searchQuery.trim()) {
        const result = await searchMemories({
          user_id: userId,
          query: searchQuery,
          project_id: projectId,
        });
        setMemories(result.memories);
      } else {
        const result = await listMemories(userId, projectId);
        setMemories(result.memories);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memories");
    } finally {
      setLoading(false);
    }
  }, [userId, projectId, searchQuery]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const handleCreate = async () => {
    if (!formContent.trim() || privateSession) return;

    try {
      const request: MemoryCreateRequest = {
        user_id: userId,
        project_id: formProjectId,
        content: formContent.trim(),
        memory_type: formType,
      };

      await createMemory(request, privateSession);
      setFormContent("");
      setShowCreateForm(false);
      loadMemories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create memory");
    }
  };

  const handleUpdate = async (id: string, updates: MemoryUpdateRequest) => {
    if (privateSession) return;

    try {
      await updateMemory(id, userId, updates, privateSession);
      setEditingId(null);
      loadMemories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update memory");
    }
  };

  const handleDelete = async (id: string) => {
    if (privateSession) return;

    if (!confirm("Are you sure you want to delete this memory?")) return;

    try {
      await deleteMemory(id, userId, privateSession);
      loadMemories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete memory");
    }
  };

  return (
    <div className={`p-4 bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Memories</h3>
        {!privateSession && (
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            {showCreateForm ? "Cancel" : "+ New Memory"}
          </button>
        )}
      </div>

      {privateSession && (
        <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-xs text-yellow-700">
            🔒 Private session: Memory operations disabled
          </p>
        </div>
      )}

      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
        />
      </div>

      {/* Create Form */}
      {showCreateForm && !privateSession && (
        <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
          <textarea
            placeholder="Memory content..."
            value={formContent}
            onChange={(e) => setFormContent(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm mb-2"
            rows={3}
          />
          <div className="flex gap-2 mb-2">
            <select
              value={formType}
              onChange={(e) =>
                setFormType(e.target.value as "fact" | "preference" | "decision")
              }
              className="px-2 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="fact">Fact</option>
              <option value="preference">Preference</option>
              <option value="decision">Decision</option>
            </select>
            <button
              onClick={handleCreate}
              className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Memory List */}
      {loading ? (
        <p className="text-sm text-gray-600">Loading memories...</p>
      ) : memories.length === 0 ? (
        <p className="text-sm text-gray-500">No memories found</p>
      ) : (
        <div className="space-y-2">
          {memories.map((memory) => (
            <MemoryItemCard
              key={memory.id}
              memory={memory}
              isEditing={editingId === memory.id}
              onEdit={() => setEditingId(memory.id)}
              onCancel={() => setEditingId(null)}
              onUpdate={(updates) => handleUpdate(memory.id, updates)}
              onDelete={() => handleDelete(memory.id)}
              privateSession={privateSession}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface MemoryItemCardProps {
  memory: MemoryItem;
  isEditing: boolean;
  onEdit: () => void;
  onCancel: () => void;
  onUpdate: (updates: MemoryUpdateRequest) => void;
  onDelete: () => void;
  privateSession: boolean;
}

function MemoryItemCard({
  memory,
  isEditing,
  onEdit,
  onCancel,
  onUpdate,
  onDelete,
  privateSession,
}: MemoryItemCardProps) {
  const [editContent, setEditContent] = useState(memory.content);
  const [editType, setEditType] = useState(memory.memory_type);

  if (isEditing) {
    return (
      <div className="p-3 bg-gray-50 rounded border border-gray-200">
        <textarea
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm mb-2"
          rows={2}
        />
        <select
          value={editType}
          onChange={(e) =>
            setEditType(e.target.value as "fact" | "preference" | "decision")
          }
          className="px-2 py-1 border border-gray-300 rounded text-sm mb-2"
        >
          <option value="fact">Fact</option>
          <option value="preference">Preference</option>
          <option value="decision">Decision</option>
        </select>
        <div className="flex gap-2">
          <button
            onClick={() => onUpdate({ content: editContent, memory_type: editType })}
            className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Save
          </button>
          <button
            onClick={onCancel}
            className="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  const typeColors = {
    fact: "bg-blue-100 text-blue-800",
    preference: "bg-green-100 text-green-800",
    decision: "bg-purple-100 text-purple-800",
  };

  return (
    <div className="p-3 bg-gray-50 rounded border border-gray-200">
      <div className="flex justify-between items-start mb-2">
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${typeColors[memory.memory_type]}`}
        >
          {memory.memory_type}
        </span>
        {!privateSession && (
          <div className="flex gap-1">
            <button
              onClick={onEdit}
              className="px-2 py-1 text-xs text-blue-600 hover:text-blue-800"
            >
              Edit
            </button>
            <button
              onClick={onDelete}
              className="px-2 py-1 text-xs text-red-600 hover:text-red-800"
            >
              Delete
            </button>
          </div>
        )}
      </div>
      <p className="text-sm text-gray-700">{memory.content}</p>
      {memory.project_id && (
        <p className="text-xs text-gray-500 mt-1">Project: {memory.project_id}</p>
      )}
      <p className="text-xs text-gray-400 mt-1">
        {new Date(memory.created_at).toLocaleDateString()}
      </p>
    </div>
  );
}

