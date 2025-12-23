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
    <div className="glass neon-border p-4 md:p-6 h-full flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Chat</h2>
        <div className="flex gap-2">
          <button
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-200/80 hover:border-neon-violet hover:text-white transition tap-target"
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
          <div className="text-slate-200/70 text-sm">Ask about your documents or start a Gemini Live session.</div>
        )}
        {messages.map(msg => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx(
              "rounded-xl px-4 py-3 border",
              msg.role === "user"
                ? "bg-white/5 border-white/10"
                : "bg-gradient-to-br from-purple-500/15 to-cyan-400/10 border-white/15"
            )}
          >
            <div className="text-xs uppercase tracking-[0.2em] text-slate-300/70 mb-1">
              {msg.role === "user" ? "You" : "Jarvis"}
            </div>
            <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
            
            {/* Uncertainty Message */}
            {msg.uncertain && (
              <div className="mt-3 p-3 bg-yellow-900/20 border border-yellow-700/50 rounded-lg">
                <div className="text-xs font-semibold text-yellow-300 mb-2">
                  ⚠️ Uncertain Response
                </div>
                {msg.reason && (
                  <div className="text-xs text-yellow-200/80 mb-2">
                    Reason: {msg.reason === "empty_retrieval" ? "No relevant information found" : "Low confidence in retrieved information"}
                  </div>
                )}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="text-xs text-yellow-200/80">
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
              <div className="mt-2 text-xs text-slate-200/70">
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
              <div className="mt-2 text-xs text-slate-200/70">
                Memories Used:
                <ul className="list-disc ml-4 space-y-0.5 mt-1">
                  {msg.memories_used.map((mem, idx) => (
                    <li key={idx}>
                      <span className="text-purple-300">{mem.type}</span>: {mem.content.substring(0, 100)}{mem.content.length > 100 ? "..." : ""}
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
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-sm focus:outline-none focus:border-neon-violet placeholder:text-slate-400/80"
          placeholder="Ask Jarvis..."
          value={text}
          onChange={e => setText(e.target.value)}
          aria-label="Chat input"
        />
        <button
          type="submit"
          onClick={handleSubmit}
          disabled={sending}
          className="glow-button px-4 py-3 text-sm disabled:opacity-60 disabled:cursor-not-allowed tap-target"
          aria-label="Send message"
        >
          {sending ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}

