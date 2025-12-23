export type Role = "user" | "assistant" | "system";

export type Source = {
  document: string;
  chunk?: number;
  score?: number;
  text?: string;
};

export type Message = {
  id: string;
  role: Role;
  content: string;
  sources?: Source[];
  uncertain?: boolean;
  reason?: string;
  suggestions?: string[];
  memories_used?: Array<{ id: string; content: string; type: string }>;
};

export type Artifact = {
  id: string;
  title: string;
  content: string;
  type?: "code" | "text";
};

