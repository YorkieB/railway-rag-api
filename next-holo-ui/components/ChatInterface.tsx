/**
 * Chat Interface Component
 * 
 * Full conversation interface with message history and context
 */

import React, { useState, useRef, useEffect } from "react";
import { Button } from "./Button";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: any[];
  memories_used?: any[];
  uncertain?: boolean;
  warning?: string;
  cost?: any;
}

interface ChatInterfaceProps {
  userId: string;
  projectId?: string;
  apiBase?: string;
}

export function ChatInterface({ 
  userId, 
  projectId, 
  apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000" 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{role: string; content: string}>>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setLoading(true);

    // Build conversation history for context
    const history = conversationHistory.concat([
      { role: "user", content: userMessage.content }
    ]);

    try {
      const response = await fetch(`${apiBase}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          user_id: userId,
          project_id: projectId,
          history: history,
          private_session: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Create assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || "No response received",
        timestamp: new Date(),
        sources: data.sources,
        memories_used: data.memories_used,
        uncertain: data.uncertain,
        warning: data.warning,
        cost: data.cost,
      };

      // Add assistant message
      setMessages((prev) => [...prev, assistantMessage]);

      // Update conversation history
      setConversationHistory((prev) => [
        ...prev,
        { role: "user", content: userMessage.content },
        { role: "assistant", content: assistantMessage.content },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Unknown error occurred. Please try again."}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationHistory([]);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Start a conversation with Jarvis</h3>
              <p className="text-sm">Ask me anything, and I'll help you!</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border dark:border-gray-700"
                }`}
              >
                <div className="whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                
                {/* Metadata for assistant messages */}
                {message.role === "assistant" && (
                  <div className="mt-3 space-y-2 text-xs">
                    {message.uncertain && (
                      <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
                        <p className="text-yellow-800 dark:text-yellow-200">
                          ⚠️ I'm not entirely certain about this answer. Please verify.
                        </p>
                      </div>
                    )}
                    
                    {message.warning && (
                      <div className="p-2 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded">
                        <p className="text-orange-800 dark:text-orange-200">
                          ⚠️ {message.warning}
                        </p>
                      </div>
                    )}

                    {message.sources && message.sources.length > 0 && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                          📚 Sources ({message.sources.length})
                        </summary>
                        <ul className="mt-2 space-y-1 pl-4">
                          {message.sources.map((source: any, idx: number) => (
                            <li key={idx} className="text-gray-600 dark:text-gray-400">
                              {source.text ? source.text.substring(0, 100) + "..." : JSON.stringify(source)}
                            </li>
                          ))}
                        </ul>
                      </details>
                    )}

                    {message.memories_used && message.memories_used.length > 0 && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                          🧠 Memories Used ({message.memories_used.length})
                        </summary>
                        <ul className="mt-2 space-y-1 pl-4">
                          {message.memories_used.map((memory: any, idx: number) => (
                            <li key={idx} className="text-gray-600 dark:text-gray-400">
                              {memory.content}
                            </li>
                          ))}
                        </ul>
                      </details>
                    )}

                    {message.cost && (
                      <div className="text-gray-500 dark:text-gray-400 mt-2">
                        💰 Cost: ${message.cost.total_cost?.toFixed(4) || "0.0000"} 
                        ({message.cost.text_tokens || 0} tokens)
                      </div>
                    )}

                    <div className="text-gray-400 dark:text-gray-500 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            className="flex-1 p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            rows={3}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <div className="flex flex-col gap-2">
            <Button
              variant="primary"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || loading}
              isLoading={loading}
            >
              Send
            </Button>
            <Button
              variant="secondary"
              onClick={clearConversation}
              disabled={messages.length === 0}
            >
              Clear
            </Button>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          {messages.length > 0 && `${messages.length} messages in conversation`}
          {conversationHistory.length > 0 && ` • ${conversationHistory.length} context messages`}
        </p>
      </div>
    </div>
  );
}

