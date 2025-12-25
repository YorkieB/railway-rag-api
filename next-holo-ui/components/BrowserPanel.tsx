/**
 * BrowserPanel Component
 * 
 * Provides browser automation UI with:
 * - Session management
 * - Navigation controls
 * - Action buttons (click, type, extract)
 * - AX Tree display
 * - Action history
 * - Safety warnings
 */

import React, { useState } from "react";
import { useBrowserSession } from "@/hooks/useBrowserSession";
import { BrowserUncertainResponse } from "@/types/browser";

interface BrowserPanelProps {
  userId?: string;
}

export function BrowserPanel({ userId }: BrowserPanelProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState("");
  const [clickSelector, setClickSelector] = useState("");
  const [typeSelector, setTypeSelector] = useState("");
  const [typeText, setTypeText] = useState("");
  const [extractSelector, setExtractSelector] = useState("");
  const [showAXTree, setShowAXTree] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const {
    session,
    axTree,
    loading,
    error,
    actionHistory,
    createSession,
    navigate,
    click,
    type,
    extract,
    close,
    refreshAXTree,
  } = useBrowserSession(sessionId, { autoRefresh: true });

  // Create new session
  const handleCreateSession = async () => {
    try {
      const newSession = await createSession({ headless: true, browser_type: "chromium" });
      setSessionId(newSession.session_id);
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  // Navigate to URL
  const handleNavigate = async () => {
    if (!urlInput.trim()) return;
    try {
      await navigate({ url: urlInput });
      setUrlInput("");
    } catch (err) {
      console.error("Navigation failed:", err);
    }
  };

  // Click element
  const handleClick = async () => {
    if (!clickSelector.trim()) return;
    try {
      const result = await click(clickSelector);
      if (result.uncertain && result.uncertain_response) {
        // Show uncertainty message
        alert(`Uncertain: ${result.uncertain_response.message}`);
      }
      setClickSelector("");
    } catch (err) {
      console.error("Click failed:", err);
    }
  };

  // Type text
  const handleType = async () => {
    if (!typeSelector.trim() || !typeText.trim()) return;
    try {
      const result = await type(typeSelector, typeText);
      if (result.uncertain && result.uncertain_response) {
        alert(`Uncertain: ${result.uncertain_response.message}`);
      }
      setTypeSelector("");
      setTypeText("");
    } catch (err) {
      console.error("Type failed:", err);
    }
  };

  // Extract text
  const handleExtract = async () => {
    if (!extractSelector.trim()) return;
    try {
      const result = await extract(extractSelector);
      if (result.success && result.details?.text) {
        alert(`Extracted text: ${result.details.text}`);
      }
      setExtractSelector("");
    } catch (err) {
      console.error("Extract failed:", err);
    }
  };

  // Close session
  const handleClose = async () => {
    try {
      await close();
      setSessionId(null);
    } catch (err) {
      console.error("Failed to close session:", err);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Browser Automation</h2>
        {session ? (
          <button
            onClick={handleClose}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Close Session
          </button>
        ) : (
          <button
            onClick={handleCreateSession}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Session"}
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {session && (
        <div className="space-y-4">
          {/* Session Info */}
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">Session ID: {session.session_id}</p>
            <p className="text-sm text-gray-600">URL: {session.current_url || "Not navigated"}</p>
            <p className="text-sm text-gray-600">Title: {session.title || "N/A"}</p>
          </div>

          {/* Navigation */}
          <div className="flex gap-2">
            <input
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Enter URL to navigate..."
              className="flex-1 px-3 py-2 border rounded"
              onKeyPress={(e) => e.key === "Enter" && handleNavigate()}
            />
            <button
              onClick={handleNavigate}
              disabled={loading || !urlInput.trim()}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              Navigate
            </button>
          </div>

          {/* Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Click */}
            <div className="p-3 border rounded">
              <h3 className="font-semibold mb-2">Click Element</h3>
              <input
                type="text"
                value={clickSelector}
                onChange={(e) => setClickSelector(e.target.value)}
                placeholder="CSS selector"
                className="w-full px-2 py-1 border rounded mb-2"
              />
              <button
                onClick={handleClick}
                disabled={loading || !clickSelector.trim()}
                className="w-full px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                Click
              </button>
            </div>

            {/* Type */}
            <div className="p-3 border rounded">
              <h3 className="font-semibold mb-2">Type Text</h3>
              <input
                type="text"
                value={typeSelector}
                onChange={(e) => setTypeSelector(e.target.value)}
                placeholder="CSS selector"
                className="w-full px-2 py-1 border rounded mb-2"
              />
              <input
                type="text"
                value={typeText}
                onChange={(e) => setTypeText(e.target.value)}
                placeholder="Text to type"
                className="w-full px-2 py-1 border rounded mb-2"
              />
              <button
                onClick={handleType}
                disabled={loading || !typeSelector.trim() || !typeText.trim()}
                className="w-full px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
              >
                Type
              </button>
            </div>

            {/* Extract */}
            <div className="p-3 border rounded">
              <h3 className="font-semibold mb-2">Extract Text</h3>
              <input
                type="text"
                value={extractSelector}
                onChange={(e) => setExtractSelector(e.target.value)}
                placeholder="CSS selector"
                className="w-full px-2 py-1 border rounded mb-2"
              />
              <button
                onClick={handleExtract}
                disabled={loading || !extractSelector.trim()}
                className="w-full px-3 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50"
              >
                Extract
              </button>
            </div>
          </div>

          {/* AX Tree Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setShowAXTree(!showAXTree);
                if (!showAXTree && !axTree) {
                  refreshAXTree();
                }
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              {showAXTree ? "Hide" : "Show"} AX Tree
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              {showHistory ? "Hide" : "Show"} History
            </button>
          </div>

          {/* AX Tree Display */}
          {showAXTree && axTree && (
            <div className="p-3 bg-gray-50 rounded max-h-96 overflow-auto">
              <h3 className="font-semibold mb-2">AX Tree</h3>
              <pre className="text-xs overflow-auto">
                {JSON.stringify(axTree.tree, null, 2)}
              </pre>
              {axTree.interactive_elements.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Interactive Elements ({axTree.interactive_elements.length})</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {axTree.interactive_elements.slice(0, 10).map((elem, idx) => (
                      <li key={idx} className="text-sm">
                        {elem.role}: {elem.name || elem.selector}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Action History */}
          {showHistory && actionHistory.length > 0 && (
            <div className="p-3 bg-gray-50 rounded max-h-96 overflow-auto">
              <h3 className="font-semibold mb-2">Action History</h3>
              <ul className="space-y-2">
                {actionHistory.slice().reverse().map((action, idx) => (
                  <li key={idx} className="text-sm p-2 bg-white rounded border">
                    <div className="flex items-center justify-between">
                      <span className={action.success ? "text-green-600" : "text-red-600"}>
                        {action.success ? "✓" : "✗"} {action.message}
                      </span>
                    </div>
                    {action.uncertain && action.uncertain_response && (
                      <div className="mt-1 text-xs text-yellow-600">
                        ⚠ {action.uncertain_response.message}
                      </div>
                    )}
                    {action.error && (
                      <div className="mt-1 text-xs text-red-600">
                        Error: {action.error}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!session && !loading && (
        <div className="text-center text-gray-500 py-8">
          No active browser session. Click "Create Session" to start.
        </div>
      )}
    </div>
  );
}

