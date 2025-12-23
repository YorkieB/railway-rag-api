import { useState } from "react";
import { apiBaseFromEnv } from "@/lib/api";
import { Message } from "@/types";

type Props = {
  apiBase: string;
  messages: Message[];
  projectName?: string;
};

export function ExportPanel({ apiBase, messages, projectName }: Props) {
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState<"conversation" | "query">("conversation");

  const exportConversation = async () => {
    setExporting(true);
    try {
      const conversation_history = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        sources: msg.sources,
        uncertain: msg.uncertain,
        reason: msg.reason,
        memories_used: msg.memories_used
      }));

      const response = await fetch(`${apiBase}/export/conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_history,
          project_name: projectName
        })
      });

      if (!response.ok) throw new Error("Export failed");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `conversation_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error("Error exporting conversation:", err);
      alert(`Export failed: ${err.message}`);
    } finally {
      setExporting(false);
    }
  };

  const exportQueryResults = async () => {
    // Find last query and answer
    const lastUserMsg = [...messages].reverse().find(m => m.role === "user");
    const lastAssistantMsg = [...messages].reverse().find(m => m.role === "assistant");

    if (!lastUserMsg || !lastAssistantMsg) {
      alert("No query results to export");
      return;
    }

    setExporting(true);
    try {
      const response = await fetch(`${apiBase}/export/query-results`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: lastUserMsg.content,
          answer: lastAssistantMsg.content,
          sources: lastAssistantMsg.sources || [],
          memories_used: lastAssistantMsg.memories_used || [],
          project_name: projectName
        })
      });

      if (!response.ok) throw new Error("Export failed");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `query_results_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error("Error exporting query results:", err);
      alert(`Export failed: ${err.message}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="glass neon-border p-4 md:p-6 space-y-4">
      <h2 className="text-xl font-semibold">Export</h2>

      <div className="space-y-3">
        <div>
          <label className="text-sm text-slate-200/70 mb-2 block">Export Type</label>
          <div className="flex gap-2">
            <button
              onClick={() => setExportType("conversation")}
              className={`px-4 py-2 text-sm rounded ${
                exportType === "conversation" ? "bg-purple-500/30" : "bg-white/5"
              }`}
              type="button"
            >
              Conversation
            </button>
            <button
              onClick={() => setExportType("query")}
              className={`px-4 py-2 text-sm rounded ${
                exportType === "query" ? "bg-purple-500/30" : "bg-white/5"
              }`}
              type="button"
            >
              Query Results
            </button>
          </div>
        </div>

        <button
          onClick={exportType === "conversation" ? exportConversation : exportQueryResults}
          className="w-full glow-button px-4 py-3 text-sm tap-target disabled:opacity-60 disabled:cursor-not-allowed"
          disabled={exporting || messages.length === 0}
          type="button"
        >
          {exporting
            ? "Exporting..."
            : exportType === "conversation"
            ? "Export Conversation"
            : "Export Query Results"}
        </button>

        {messages.length === 0 && (
          <div className="text-xs text-slate-400">No messages to export</div>
        )}
      </div>
    </div>
  );
}

