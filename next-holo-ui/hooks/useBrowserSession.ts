/**
 * React Hook for Browser Session Management
 */

import { useState, useEffect, useCallback } from "react";
import {
  BrowserSession,
  BrowserSessionCreate,
  NavigateRequest,
  AXTreeResponse,
  ActionResponse,
  PlanRequest,
} from "@/types/browser";
import {
  createBrowserSession,
  getBrowserSession,
  closeBrowserSession,
  navigateBrowser,
  getAXTree,
  clickElement,
  typeText,
  extractText,
  executePlan,
} from "@/lib/api-browser";

interface UseBrowserSessionOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function useBrowserSession(
  sessionId: string | null,
  options: UseBrowserSessionOptions = {}
) {
  const { autoRefresh = false, refreshInterval = 5000 } = options;

  const [session, setSession] = useState<BrowserSession | null>(null);
  const [axTree, setAXTree] = useState<AXTreeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionHistory, setActionHistory] = useState<ActionResponse[]>([]);

  // Fetch session status
  const fetchSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await getBrowserSession(sessionId);
      setSession(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch session");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Fetch AX tree
  const fetchAXTree = useCallback(async (includeHidden: boolean = false) => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await getAXTree(sessionId, includeHidden);
      setAXTree(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch AX tree");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Auto-refresh session
  useEffect(() => {
    if (!sessionId || !autoRefresh) return;

    fetchSession();
    const interval = setInterval(fetchSession, refreshInterval);
    return () => clearInterval(interval);
  }, [sessionId, autoRefresh, refreshInterval, fetchSession]);

  // Create session
  const createSession = useCallback(async (data: BrowserSessionCreate = {}) => {
    try {
      setLoading(true);
      setError(null);
      const newSession = await createBrowserSession(data);
      setSession(newSession);
      return newSession;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create session";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Navigate
  const navigate = useCallback(async (data: NavigateRequest) => {
    if (!sessionId) throw new Error("No session active");

    try {
      setLoading(true);
      setError(null);
      const result = await navigateBrowser(sessionId, data);
      
      // Refresh session after navigation
      await fetchSession();
      await fetchAXTree();
      
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Navigation failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId, fetchSession, fetchAXTree]);

  // Click element
  const click = useCallback(async (selector: string, verify: boolean = true) => {
    if (!sessionId) throw new Error("No session active");

    try {
      setLoading(true);
      setError(null);
      const result = await clickElement(sessionId, { selector, verify });
      setActionHistory((prev) => [...prev, result]);
      
      // Refresh AX tree after action
      await fetchAXTree();
      
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Click failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId, fetchAXTree]);

  // Type text
  const type = useCallback(async (selector: string, text: string, clearFirst: boolean = true) => {
    if (!sessionId) throw new Error("No session active");

    try {
      setLoading(true);
      setError(null);
      const result = await typeText(sessionId, { selector, text, clear_first: clearFirst });
      setActionHistory((prev) => [...prev, result]);
      
      // Refresh AX tree after action
      await fetchAXTree();
      
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Type failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId, fetchAXTree]);

  // Extract text
  const extract = useCallback(async (selector: string) => {
    if (!sessionId) throw new Error("No session active");

    try {
      setLoading(true);
      setError(null);
      const result = await extractText(sessionId, { selector });
      setActionHistory((prev) => [...prev, result]);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Extract failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Execute plan
  const execute = useCallback(async (data: PlanRequest) => {
    if (!sessionId) throw new Error("No session active");

    try {
      setLoading(true);
      setError(null);
      const result = await executePlan(sessionId, data);
      
      // Refresh AX tree after plan execution
      await fetchAXTree();
      
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Plan execution failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId, fetchAXTree]);

  // Close session
  const close = useCallback(async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);
      await closeBrowserSession(sessionId);
      setSession(null);
      setAXTree(null);
      setActionHistory([]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to close session";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return {
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
    execute,
    close,
    refreshSession: fetchSession,
    refreshAXTree: fetchAXTree,
  };
}

