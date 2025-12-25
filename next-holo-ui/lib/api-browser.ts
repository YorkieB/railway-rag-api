/**
 * Browser Automation API Client
 */

import {
  BrowserSession,
  BrowserSessionCreate,
  NavigateRequest,
  NavigateResponse,
  AXTreeResponse,
  ClickRequest,
  TypeRequest,
  ExtractRequest,
  ActionResponse,
  PlanRequest,
  PlanResponse,
} from "@/types/browser";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

/**
 * Create a new browser session
 */
export async function createBrowserSession(
  data: BrowserSessionCreate = {}
): Promise<BrowserSession> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to create session" }));
    throw new Error(error.detail || "Failed to create browser session");
  }

  return response.json();
}

/**
 * Get browser session status
 */
export async function getBrowserSession(sessionId: string): Promise<BrowserSession> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Session not found" }));
    throw new Error(error.detail || "Failed to get browser session");
  }

  return response.json();
}

/**
 * List all browser sessions
 */
export async function listBrowserSessions(): Promise<BrowserSession[]> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions`);

  if (!response.ok) {
    throw new Error("Failed to list browser sessions");
  }

  const data = await response.json();
  return data.sessions || [];
}

/**
 * Navigate to URL
 */
export async function navigateBrowser(
  sessionId: string,
  data: NavigateRequest
): Promise<NavigateResponse> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}/navigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Navigation failed" }));
    throw new Error(error.detail || "Failed to navigate");
  }

  return response.json();
}

/**
 * Get AX tree for current page
 */
export async function getAXTree(
  sessionId: string,
  includeHidden: boolean = false
): Promise<AXTreeResponse> {
  const response = await fetch(
    `${API_BASE_URL}/browser/sessions/${sessionId}/ax-tree?include_hidden=${includeHidden}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to get AX tree" }));
    throw new Error(error.detail || "Failed to get AX tree");
  }

  return response.json();
}

/**
 * Click element
 */
export async function clickElement(
  sessionId: string,
  data: ClickRequest
): Promise<ActionResponse> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}/actions/click`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Click failed" }));
    throw new Error(error.detail || "Failed to click element");
  }

  return response.json();
}

/**
 * Type text into input
 */
export async function typeText(
  sessionId: string,
  data: TypeRequest
): Promise<ActionResponse> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}/actions/type`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Type failed" }));
    throw new Error(error.detail || "Failed to type text");
  }

  return response.json();
}

/**
 * Extract text from element
 */
export async function extractText(
  sessionId: string,
  data: ExtractRequest
): Promise<ActionResponse> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}/actions/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Extract failed" }));
    throw new Error(error.detail || "Failed to extract text");
  }

  return response.json();
}

/**
 * Execute action plan
 */
export async function executePlan(
  sessionId: string,
  data: PlanRequest
): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}/actions/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Plan execution failed" }));
    throw new Error(error.detail || "Failed to execute plan");
  }

  return response.json();
}

/**
 * Close browser session
 */
export async function closeBrowserSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/browser/sessions/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to close session" }));
    throw new Error(error.detail || "Failed to close browser session");
  }
}

