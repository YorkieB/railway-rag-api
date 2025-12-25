/**
 * Budget and Cost Types
 */

export interface BudgetStatus {
  user_id: string;
  date: string;
  text_tokens: {
    used: number;
    limit: number;
    remaining: number;
    utilization: number;
  };
  vision_tokens: {
    used: number;
    limit: number;
    remaining: number;
    utilization: number;
  };
  audio_minutes: {
    used: number;
    limit: number;
    remaining: number;
    utilization: number;
  };
  dollars: {
    used: number;
    limit: number;
    remaining: number;
    utilization: number;
  };
  warnings: string[];
  is_exceeded: boolean;
  should_warn: boolean;
}

export interface CostInfo {
  text_tokens: number;
  vision_tokens: number;
  audio_minutes: number;
  text_cost: number;
  vision_cost: number;
  audio_cost: number;
  total_cost: number;
}

