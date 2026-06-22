export type DecisionType = "APPROVED" | "PARTIAL" | "REJECTED" | "MANUAL_REVIEW";
export type AgentStatus = "PENDING" | "SUCCESS" | "FAILED" | "SKIPPED" | "DEGRADED";

export const CLAIM_CATEGORIES = [
  "CONSULTATION", 
  "DIAGNOSTIC", 
  "PHARMACY", 
  "DENTAL", 
  "VISION", 
  "ALTERNATIVE_MEDICINE"
] as const;

export type ClaimCategory = typeof CLAIM_CATEGORIES[number];

export interface LineItem {
  description: string;
  amount: number;
  is_covered: boolean;
  rejection_reason?: string;
}

export interface ConfidenceEvent {
  agent_name: string;
  timestamp: string;
  penalty_applied: number;
  reason: string;
}

export interface AgentTrace {
  agent_name: string;
  start_time: string;
  end_time?: string;
  execution_time_ms?: number;
  status: AgentStatus;
  warnings: string[];
  errors: string[];
  decision_impact?: string;
  extracted_keys: string[];
}

export interface SystemTrace {
  claim_id: string;
  overall_status: string;
  base_confidence: number;
  current_confidence_score: number;
  confidence_ledger: ConfidenceEvent[];
  agent_traces: AgentTrace[];
}

export interface ClaimResult {
  decision: DecisionType | null;
  approved_amount: number;
  rejection_reasons: string[];
  line_items: LineItem[];
  notes: string[];
}

export interface ClaimContextPayload {
  trace: SystemTrace;
  result: ClaimResult;
  state: {
    is_halted: boolean;
    halt_reason?: string;
    halt_message?: string;
  };
}