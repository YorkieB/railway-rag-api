import { FormEvent, MouseEvent, useRef, useState } from "react";
import { Message } from "@/types";
import { motion } from "framer-motion";
import clsx from "clsx";

type ChatPanelProps = {
  messages: Message[];
  onSend: (text: string) => Promise<void> | void;
  sending?: boolean;
  onFileSelected?: (file: File) => Promise<void> | void;
};

export function ChatPanel({ messages, onSend, sending, onFileSelected }: ChatPanelProps) {
  const [text, setText] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (e?: FormEvent | MouseEvent) => {
    e?.preventDefault?.();
    if (!text.trim()) return;
    await onSend(text.trim());
    setText("");
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileSelected) onFileSelected(file);
    e.target.value = "";
  };

  return (
    <div className="card p-4 md:p-6 h-full flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Chat</h2>
        <div className="flex gap-2">
          <button
            className="btn-secondary text-sm tap-target"
            onClick={() => fileInputRef.current?.click()}
            aria-label="Upload document to knowledge base"
          >
            Upload
          </button>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md"
            ref={fileInputRef}
            className="hidden"
            onChange={handleFile}
          />
        </div>
      </div>

      <div
        className="flex-1 min-h-[380px] md:min-h-[420px] max-h-[540px] xl:max-h-[640px] overflow-y-auto space-y-3 pr-1"
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
      >
        {messages.length === 0 && (
          <div className="text-gray-500 text-sm">Ask about your documents or start a conversation.</div>
        )}
        {messages.map(msg => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx(
              "rounded-lg px-4 py-3 border",
              msg.role === "user"
                ? "bg-gray-50 border-gray-200"
                : "bg-white border-gray-200"
            )}
          >
            <div className="text-xs uppercase tracking-wide text-gray-500 mb-1.5 font-medium">
              {msg.role === "user" ? "You" : "Jarvis"}
            </div>
            <div className="whitespace-pre-wrap leading-relaxed text-gray-900">{msg.content}</div>
            
            {/* Uncertainty Message */}
            {msg.uncertain && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-xs font-semibold text-yellow-800 mb-2">
                  ⚠️ Uncertain Response
                </div>
                {msg.reason && (
                  <div className="text-xs text-yellow-700 mb-2">
                    Reason: {msg.reason === "empty_retrieval" ? "No relevant information found" : "Low confidence in retrieved information"}
                  </div>
                )}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="text-xs text-yellow-700">
                    Suggestions:
                    <ul className="list-disc ml-4 mt-1 space-y-1">
                      {msg.suggestions.map((suggestion, idx) => (
                        <li key={idx}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {/* Sources */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 text-xs text-gray-600">
                Sources:
                <ul className="list-disc ml-4 space-y-0.5 mt-1">
                  {msg.sources.map((s, idx) => (
                    <li key={idx}>
                      {s.document} {s.score ? `(score ${s.score.toFixed(3)})` : ""} {s.chunk !== undefined ? `chunk ${s.chunk}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Memory Citations */}
            {msg.memories_used && msg.memories_used.length > 0 && (
              <div className="mt-2 text-xs text-gray-600">
                Memories Used:
                <ul className="list-disc ml-4 space-y-0.5 mt-1">
                  {msg.memories_used.map((mem, idx) => (
                    <li key={idx}>
                      <span className="text-primary font-medium">{mem.type}</span>: {mem.content.substring(0, 100)}{mem.content.length > 100 ? "..." : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 items-center">
        <input
          className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-gray-400"
          placeholder="Ask Jarvis..."
          value={text}
          onChange={e => setText(e.target.value)}
          aria-label="Chat input"
        />
        <button
          type="submit"
          onClick={handleSubmit}
          disabled={sending}
          className="btn-primary text-sm disabled:opacity-60 disabled:cursor-not-allowed tap-target"
          aria-label="Send message"
        >
          {sending ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}

