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
  const [pageInfo, setPageInfo] = useState<any>(null);
  
  const navigateUrlRef = useRef<HTMLInputElement>(null);
  const clickRoleRef = useRef<HTMLInputElement>(null);
  const clickNameRef = useRef<HTMLInputElement>(null);
  const typeRoleRef = useRef<HTMLInputElement>(null);
  const typeNameRef = useRef<HTMLInputElement>(null);
  const typeTextRef = useRef<HTMLInputElement>(null);
  const loginUrlRef = useRef<HTMLInputElement>(null);
  const loginUsernameRef = useRef<HTMLInputElement>(null);
  const loginPasswordRef = useRef<HTMLInputElement>(null);

  const statusChip = {
    idle: { label: "Idle", color: "bg-gray-400" },
    connecting: { label: "Connecting...", color: "bg-yellow-500" },
    active: { label: "Active", color: "bg-green-500 animate-pulse" },
    error: { label: "Error", color: "bg-red-500" }
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
      await refreshPageInfo();
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

  const refreshPageInfo = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/page-info`);
      if (response.ok) {
        const data = await response.json();
        setPageInfo(data);
        setCurrentUrl(data.url || "");
      }
    } catch (err) {
      console.error("Error getting page info:", err);
    }
  };

  const normalizeUrl = (input: string): string => {
    // Remove whitespace
    input = input.trim();
    
    // If it already has a protocol, return as-is
    if (/^https?:\/\//i.test(input)) {
      return input;
    }
    
    // If it looks like a domain (has dots and no spaces), add https://
    if (/^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}/.test(input)) {
      return `https://${input}`;
    }
    
    // Otherwise, treat as a search query and use Google search
    return `https://www.google.com/search?q=${encodeURIComponent(input)}`;
  };

  const navigate = async () => {
    if (!sessionId || !navigateUrlRef.current?.value) return;
    
    const rawUrl = navigateUrlRef.current.value;
    const url = normalizeUrl(rawUrl);
    
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
        await refreshPageInfo();
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
        await refreshPageInfo();
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
        await refreshPageInfo();
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

  const automateLogin = async () => {
    if (!sessionId || !loginUsernameRef.current?.value || !loginPasswordRef.current?.value) {
      setSafetyWarnings(prev => [...prev, "Username and password are required"]);
      return;
    }
    
    const username = loginUsernameRef.current.value;
    const password = loginPasswordRef.current.value;
    const url = loginUrlRef.current?.value || undefined;
    
    try {
      const body: any = { username, password };
      if (url) body.url = url;
      
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/actions/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      
      setActionHistory(prev => [...prev, {
        id: Math.random().toString(36).slice(2),
        timestamp: Date.now(),
        action: `Login${url ? ` to ${url}` : ""}`,
        result: data
      }]);
      
      if (data.success) {
        await refreshScreenshot();
        await refreshAxTree();
        await refreshPageInfo();
        // Clear password field for security
        if (loginPasswordRef.current) loginPasswordRef.current.value = "";
      } else {
        setSafetyWarnings(prev => [...prev, data.error || "Login failed"]);
      }
    } catch (err: any) {
      console.error("Error during login:", err);
      setStatus("error");
    }
  };

  const findLoginFields = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${apiBase}/browser/sessions/${sessionId}/actions/login/find-fields`, {
        method: "POST"
      });
      
      const data = await response.json();
      
      if (data.found) {
        setActionHistory(prev => [...prev, {
          id: Math.random().toString(36).slice(2),
          timestamp: Date.now(),
          action: "Find login fields",
          result: { 
            found: true,
            username_field: data.username_field?.name || "Found",
            password_field: data.password_field?.name || "Found"
          }
        }]);
      } else {
        setUncertaintyMessages(prev => [...prev, "Could not find login fields on this page"]);
      }
    } catch (err: any) {
      console.error("Error finding login fields:", err);
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
    <div className="card p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-xl font-semibold text-gray-900">Browser Automation</h2>
        <span className="chip">
          <span className={`inline-block h-2 w-2 rounded-full ${statusChip.color} mr-2`} aria-hidden="true" />
          {statusChip.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        {status === "idle" ? (
          <button
            onClick={createSession}
            className="btn-primary text-sm tap-target"
            type="button"
          >
            Start Browser Session
          </button>
        ) : (
          <button
            onClick={closeSession}
            className="btn-secondary text-sm tap-target bg-red-50 text-red-700 border-red-200 hover:bg-red-100"
            type="button"
          >
            Close Session
          </button>
        )}
        {status === "active" && (
          <>
            <button
              onClick={refreshScreenshot}
              className="btn-secondary text-sm tap-target"
              type="button"
            >
              Refresh
            </button>
            <button
              onClick={() => setShowAxTree(!showAxTree)}
              className="btn-secondary text-sm tap-target"
              type="button"
            >
              {showAxTree ? "Hide" : "Show"} AX Tree
            </button>
          </>
        )}
      </div>

      {safetyWarnings.length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 space-y-1">
          <div className="text-xs font-semibold text-red-800">Safety Warnings</div>
          {safetyWarnings.map((warning, idx) => (
            <div key={idx} className="text-sm text-red-700">{warning}</div>
          ))}
        </div>
      )}

      {uncertaintyMessages.length > 0 && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3 space-y-1">
          <div className="text-xs font-semibold text-yellow-800">Uncertainty Messages</div>
          {uncertaintyMessages.map((msg, idx) => (
            <div key={idx} className="text-sm text-yellow-700">{msg}</div>
          ))}
        </div>
      )}

      {status === "active" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            <div className="space-y-2">
              <div className="text-xs text-gray-600">Browser Viewport</div>
              <div className="rounded-lg overflow-hidden border border-gray-200 bg-gray-100">
                {screenshot ? (
                  <img
                    src={`data:image/png;base64,${screenshot}`}
                    alt="Browser screenshot"
                    className="w-full h-auto"
                  />
                ) : (
                  <div className="p-8 text-center text-gray-500">Loading screenshot...</div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-xs text-gray-600">Navigate</div>
              <div className="flex gap-2">
                <input
                  ref={navigateUrlRef}
                  type="text"
                  placeholder="https://example.com"
                  className="flex-1 bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  onKeyPress={(e) => e.key === "Enter" && navigate()}
                />
                <button
                  onClick={navigate}
                  className="btn-primary text-sm"
                  type="button"
                >
                  Go
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="text-xs text-gray-600">Click Element</div>
                <input
                  ref={clickRoleRef}
                  type="text"
                  placeholder="Role (e.g., button)"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <input
                  ref={clickNameRef}
                  type="text"
                  placeholder="Name (e.g., Search)"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <button
                  onClick={clickElement}
                  className="w-full btn-primary text-sm"
                  type="button"
                >
                  Click
                </button>
              </div>

              <div className="space-y-2">
                <div className="text-xs text-gray-600">Type Text</div>
                <input
                  ref={typeRoleRef}
                  type="text"
                  placeholder="Role (e.g., textbox)"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <input
                  ref={typeNameRef}
                  type="text"
                  placeholder="Name (e.g., Search)"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <input
                  ref={typeTextRef}
                  type="text"
                  placeholder="Text to type"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <button
                  onClick={typeText}
                  className="w-full btn-primary text-sm"
                  type="button"
                >
                  Type
                </button>
              </div>

              <div className="space-y-2 border-t border-gray-200 pt-4">
                <div className="text-xs text-gray-600 font-semibold">🔐 Login Automation</div>
                <input
                  ref={loginUrlRef}
                  type="text"
                  placeholder="Login URL (optional if already on page)"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <input
                  ref={loginUsernameRef}
                  type="text"
                  placeholder="Username or Email"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <input
                  ref={loginPasswordRef}
                  type="password"
                  placeholder="Password"
                  className="w-full bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 mb-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <div className="flex gap-2">
                  <button
                    onClick={findLoginFields}
                    className="flex-1 btn-secondary text-sm"
                    type="button"
                  >
                    Find Fields
                  </button>
                  <button
                    onClick={automateLogin}
                    className="flex-1 btn-primary text-sm"
                    type="button"
                  >
                    Sign In
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {showAxTree && (
              <div className="space-y-2">
                <div className="text-xs text-gray-600">AX Tree ({axTree.length} elements)</div>
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-2 max-h-64 overflow-y-auto">
                  {axTree.slice(0, 50).map((node, idx) => (
                    <div
                      key={idx}
                      className="text-xs text-gray-700 mb-1 cursor-pointer hover:bg-gray-100 p-1 rounded transition-colors"
                      onClick={() => extractText(node.role, node.name)}
                    >
                      <span className="text-primary font-medium">{node.role}</span>: {node.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <div className="text-xs text-gray-600">Action History</div>
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-2 max-h-64 overflow-y-auto space-y-2">
                {actionHistory.length === 0 ? (
                  <div className="text-xs text-gray-500">No actions yet</div>
                ) : (
                  actionHistory.slice().reverse().map((action) => (
                    <div key={action.id} className="text-xs text-gray-700 border-l-2 border-primary/50 pl-2">
                      <div className="font-semibold">{action.action}</div>
                      <div className="text-gray-500">
                        {new Date(action.timestamp).toLocaleTimeString()}
                      </div>
                      {action.result.success === false && (
                        <div className="text-red-600 text-xs mt-1">
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

