import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { apiBaseFromEnv } from "@/lib/api";

type Props = {
  apiBase: string;
};

type BrowserStatus = "idle" | "connecting" | "active" | "error";

type AxTreeNode = {
  id: string;
  role: string;
  name: string;
  bounds?: { x: number; y: number; width: number; height: number };
};

type ActionHistory = Array<{
  id: string;
  timestamp: number;
  action: string;
  result: any;
}>;

export function BrowserPanel({ apiBase }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<BrowserStatus>("idle");
  const [currentUrl, setCurrentUrl] = useState("");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [axTree, setAxTree] = useState<AxTreeNode[]>([]);
  const [showAxTree, setShowAxTree] = useState(false);
  const [actionHistory, setActionHistory] = useState<ActionHistory>([]);
  const [safetyWarnings, setSafetyWarnings] = useState<string[]>([]);
  const [uncertaintyMessages, setUncertaintyMessages] = useState<string[]>([]);
  
  const navigateUrlRef = useRef<HTMLInputElement>(null);
  const clickRoleRef = useRef<HTMLInputElement>(null);
  const clickNameRef = useRef<HTMLInputElement>(null);
  const typeRoleRef = useRef<HTMLInputElement>(null);
  const typeNameRef = useRef<HTMLInputElement>(null);
  const typeTextRef = useRef<HTMLInputElement>(null);

  const statusChip = {
    idle: { label: "Idle", color: "bg-slate-300" },
    connecting: { label: "Connecting...", color: "bg-amber-300" },
    active: { label: "Active", color: "bg-emerald-400 animate-pulse" },
    error: { label: "Error", color: "bg-red-400" }
  }[status];

  const createSession = async () => {
    try {
      setStatus("connecting");
      const response = await fetch(`${apiBase}/browser/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (!response.ok) throw new Error("Failed to create session");
      
      const data = await response.json();
      setSessionId(data.session_id);
      setStatus("active");
      await refreshScreenshot();
      await refreshAxTree();
    } catch (err: any) {
      console.error("Error creating session:", err);
      setStatus("error");
    }
  };

  const closeSession = async () => {
    if (sessionId) {
      try {
        await fetch(`${apiBase}/browser/sessions/${sessionId}`, { method: "DELETE" });
      } catch (err) {
        console.error("Error closing session:", err);
      }
    }
    setSessionId(null);
    setStatus("idle");
    setScreenshot(null);
    setAxTree([]);
    setActionHistory([]);
    setSafetyWarnings([]);
    setUncertaintyMessages([]);
  };

  const refreshScreenshot = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/screenshot`);
      if (response.ok) {
        const data = await response.json();
        setScreenshot(data.screenshot);
      }
    } catch (err) {
      console.error("Error getting screenshot:", err);
    }
  };

  const refreshAxTree = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/ax-tree`);
      if (response.ok) {
        const data = await response.json();
        setAxTree(data.ax_tree || []);
      }
    } catch (err) {
      console.error("Error getting AX tree:", err);
    }
  };

  const navigate = async () => {
    if (!sessionId || !navigateUrlRef.current?.value) return;
    
    const url = navigateUrlRef.current.value;
    try {
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/navigate?url=${encodeURIComponent(url)}`, {
        method: "POST"
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setCurrentUrl(data.url || url);
        setActionHistory(prev => [...prev, {
          id: Math.random().toString(36).slice(2),
          timestamp: Date.now(),
          action: `Navigate to ${url}`,
          result: data
        }]);
        await refreshScreenshot();
        await refreshAxTree();
      } else {
        setSafetyWarnings(prev => [...prev, data.detail || "Navigation blocked"]);
      }
    } catch (err: any) {
      console.error("Error navigating:", err);
      setStatus("error");
    }
  };

  const clickElement = async () => {
    if (!sessionId || !clickNameRef.current?.value) return;
    
    const role = clickRoleRef.current?.value || undefined;
    const name = clickNameRef.current.value;
    
    try {
      const params = new URLSearchParams({ name });
      if (role) params.append("role", role);
      
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/actions/click?${params.toString()}`, {
        method: "POST"
      });
      
      const data = await response.json();
      
      setActionHistory(prev => [...prev, {
        id: Math.random().toString(36).slice(2),
        timestamp: Date.now(),
        action: `Click ${name}`,
        result: data
      }]);
      
      if (data.uncertain) {
        setUncertaintyMessages(prev => [...prev, data.message || "Element not found"]);
      }
      
      if (data.blocked) {
        setSafetyWarnings(prev => [...prev, data.message || "Action blocked"]);
      }
      
      if (data.success) {
        await refreshScreenshot();
        await refreshAxTree();
      }
    } catch (err: any) {
      console.error("Error clicking:", err);
    }
  };

  const typeText = async () => {
    if (!sessionId || !typeTextRef.current?.value || !typeNameRef.current?.value) return;
    
    const role = typeRoleRef.current?.value || undefined;
    const name = typeNameRef.current.value;
    const text = typeTextRef.current.value;
    
    try {
      const params = new URLSearchParams({ text, name });
      if (role) params.append("role", role);
      
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/actions/type?${params.toString()}`, {
        method: "POST"
      });
      
      const data = await response.json();
      
      setActionHistory(prev => [...prev, {
        id: Math.random().toString(36).slice(2),
        timestamp: Date.now(),
        action: `Type "${text}" into ${name}`,
        result: data
      }]);
      
      if (data.uncertain) {
        setUncertaintyMessages(prev => [...prev, data.message || "Element not found"]);
      }
      
      if (data.blocked) {
        setSafetyWarnings(prev => [...prev, data.message || "Action blocked"]);
      }
      
      if (data.success) {
        await refreshScreenshot();
        await refreshAxTree();
      }
    } catch (err: any) {
      console.error("Error typing:", err);
    }
  };

  const extractText = async (role?: string, name?: string) => {
    if (!sessionId) return;
    
    try {
      const params = new URLSearchParams();
      if (role) params.append("role", role);
      if (name) params.append("name", name);
      
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/actions/extract?${params.toString()}`, {
        method: "POST"
      });
      
      const data = await response.json();
      
      if (data.success && data.text) {
        setActionHistory(prev => [...prev, {
          id: Math.random().toString(36).slice(2),
          timestamp: Date.now(),
          action: `Extract text from ${name || "element"}`,
          result: { text: data.text }
        }]);
      }
    } catch (err: any) {
      console.error("Error extracting:", err);
    }
  };

  useEffect(() => {
    if (status === "active" && sessionId) {
      const interval = setInterval(() => {
        refreshScreenshot();
        refreshAxTree();
      }, 2000); // Refresh every 2 seconds
      return () => clearInterval(interval);
    }
  }, [status, sessionId]);

  return (
    <div className="glass neon-border p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-xl font-semibold">Browser Automation</h2>
        <span className="chip">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${statusChip.color}`} aria-hidden="true" />
          {statusChip.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        {status === "idle" ? (
          <button
            onClick={createSession}
            className="glow-button px-4 py-3 text-sm tap-target"
            type="button"
          >
            Start Browser Session
          </button>
        ) : (
          <button
            onClick={closeSession}
            className="glow-button px-4 py-3 text-sm tap-target bg-red-500/70 hover:bg-red-500/90"
            type="button"
          >
            Close Session
          </button>
        )}
        {status === "active" && (
          <>
            <button
              onClick={refreshScreenshot}
              className="glow-button px-4 py-3 text-sm tap-target"
              type="button"
            >
              Refresh
            </button>
            <button
              onClick={() => setShowAxTree(!showAxTree)}
              className="glow-button px-4 py-3 text-sm tap-target"
              type="button"
            >
              {showAxTree ? "Hide" : "Show"} AX Tree
            </button>
          </>
        )}
      </div>

      {safetyWarnings.length > 0 && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 space-y-1">
          <div className="text-xs font-semibold text-red-300">Safety Warnings</div>
          {safetyWarnings.map((warning, idx) => (
            <div key={idx} className="text-sm text-red-200">{warning}</div>
          ))}
        </div>
      )}

      {uncertaintyMessages.length > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 space-y-1">
          <div className="text-xs font-semibold text-amber-300">Uncertainty Messages</div>
          {uncertaintyMessages.map((msg, idx) => (
            <div key={idx} className="text-sm text-amber-200">{msg}</div>
          ))}
        </div>
      )}

      {status === "active" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            <div className="space-y-2">
              <div className="text-xs text-slate-200/70">Browser Viewport</div>
              <div className="rounded-lg overflow-hidden border border-white/10 bg-black/40">
                {screenshot ? (
                  <img
                    src={`data:image/png;base64,${screenshot}`}
                    alt="Browser screenshot"
                    className="w-full h-auto"
                  />
                ) : (
                  <div className="p-8 text-center text-slate-400">Loading screenshot...</div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-xs text-slate-200/70">Navigate</div>
              <div className="flex gap-2">
                <input
                  ref={navigateUrlRef}
                  type="text"
                  placeholder="https://example.com"
                  className="flex-1 bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400"
                  onKeyPress={(e) => e.key === "Enter" && navigate()}
                />
                <button
                  onClick={navigate}
                  className="glow-button px-4 py-2 text-sm"
                  type="button"
                >
                  Go
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="text-xs text-slate-200/70">Click Element</div>
                <input
                  ref={clickRoleRef}
                  type="text"
                  placeholder="Role (e.g., button)"
                  className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400 mb-2"
                />
                <input
                  ref={clickNameRef}
                  type="text"
                  placeholder="Name (e.g., Search)"
                  className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400 mb-2"
                />
                <button
                  onClick={clickElement}
                  className="w-full glow-button px-4 py-2 text-sm"
                  type="button"
                >
                  Click
                </button>
              </div>

              <div className="space-y-2">
                <div className="text-xs text-slate-200/70">Type Text</div>
                <input
                  ref={typeRoleRef}
                  type="text"
                  placeholder="Role (e.g., textbox)"
                  className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400 mb-2"
                />
                <input
                  ref={typeNameRef}
                  type="text"
                  placeholder="Name (e.g., Search)"
                  className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400 mb-2"
                />
                <input
                  ref={typeTextRef}
                  type="text"
                  placeholder="Text to type"
                  className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400 mb-2"
                />
                <button
                  onClick={typeText}
                  className="w-full glow-button px-4 py-2 text-sm"
                  type="button"
                >
                  Type
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {showAxTree && (
              <div className="space-y-2">
                <div className="text-xs text-slate-200/70">AX Tree ({axTree.length} elements)</div>
                <div className="rounded-lg border border-white/10 bg-black/40 p-2 max-h-64 overflow-y-auto">
                  {axTree.slice(0, 50).map((node, idx) => (
                    <div
                      key={idx}
                      className="text-xs text-slate-300 mb-1 cursor-pointer hover:bg-white/5 p-1 rounded"
                      onClick={() => extractText(node.role, node.name)}
                    >
                      <span className="text-purple-300">{node.role}</span>: {node.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <div className="text-xs text-slate-200/70">Action History</div>
              <div className="rounded-lg border border-white/10 bg-black/40 p-2 max-h-64 overflow-y-auto space-y-2">
                {actionHistory.length === 0 ? (
                  <div className="text-xs text-slate-400">No actions yet</div>
                ) : (
                  actionHistory.slice().reverse().map((action) => (
                    <div key={action.id} className="text-xs text-slate-300 border-l-2 border-purple-500/50 pl-2">
                      <div className="font-semibold">{action.action}</div>
                      <div className="text-slate-400">
                        {new Date(action.timestamp).toLocaleTimeString()}
                      </div>
                      {action.result.success === false && (
                        <div className="text-red-400 text-xs mt-1">
                          {action.result.error || action.result.message}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

