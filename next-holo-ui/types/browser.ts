/**
 * Browser Automation Types
 */

export interface BrowserSession {
  session_id: string;
  is_active: boolean;
  current_url: string | null;
  title: string | null;
}

export interface BrowserSessionCreate {
  headless?: boolean;
  browser_type?: "chromium" | "firefox" | "webkit";
}

export interface NavigateRequest {
  url: string;
  wait_until?: "load" | "domcontentloaded" | "networkidle" | "commit";
  timeout?: number;
}

export interface NavigateResponse {
  success: boolean;
  url?: string;
  title?: string;
  status?: number;
  error?: string;
  safety_violation?: SafetyViolation;
}

export interface SafetyViolation {
  type: string;
  severity: "error" | "warning";
  message: string;
}

export interface AXTreeNode {
  role: string;
  name?: string;
  value?: string;
  description?: string;
  state?: Record<string, boolean>;
  selector?: string;
  children?: AXTreeNode[];
}

export interface AXTreeResponse {
  session_id: string;
  tree: AXTreeNode;
  interactive_elements: AXTreeNode[];
}

export interface ClickRequest {
  selector: string;
  verify?: boolean;
  timeout?: number;
}

export interface TypeRequest {
  selector: string;
  text: string;
  clear_first?: boolean;
  verify?: boolean;
  timeout?: number;
}

export interface ExtractRequest {
  selector: string;
  timeout?: number;
}

export interface ActionResponse {
  success: boolean;
  message: string;
  element_found: boolean;
  verification_passed: boolean;
  error?: string;
  details?: Record<string, any>;
  uncertain: boolean;
  uncertain_response?: BrowserUncertainResponse;
}

export interface BrowserUncertainResponse {
  uncertain: boolean;
  message: string;
  suggestions?: string[];
  reason: string;
  details?: Record<string, any>;
}

export interface PlanRequest {
  action: "click" | "type" | "extract";
  target: string;
  expected_outcome: string;
  max_retries?: number;
}

export interface PlanResponse {
  success: boolean;
  attempts: number;
  recovered: boolean;
  result: {
    success: boolean;
    message: string;
    error?: string;
  };
  history: Array<{
    action: string;
    target: string;
    attempts: number;
    success: boolean;
    recovered: boolean;
    error?: string;
  }>;
}

