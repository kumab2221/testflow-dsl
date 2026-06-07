// TestFlow DSL の TypeScript 型定義
// schemas/testflow-dsl.schema.json に準拠する

export type OperandSource =
  | "backendInput"
  | "observed"
  | "internal"
  | "derived"
  | "reference"
  | "clock";

export interface SignalOperand {
  source: OperandSource;
  signal: string;
}

export interface ValueOperand {
  value: string | number | boolean | null;
}

export type Operand = SignalOperand | ValueOperand;

// --------------------------------------------------------------------------
// Condition
// --------------------------------------------------------------------------

export type ComparisonOperator =
  | "equals"
  | "notEquals"
  | "greaterThan"
  | "greaterThanOrEqual"
  | "lessThan"
  | "lessThanOrEqual";

export interface ComparisonCondition {
  type: "comparison";
  left: Operand;
  operator: ComparisonOperator;
  right: Operand;
  unit?: string;
}

export type TimeoutClock =
  | "elapsedBlockSimulationTime"
  | "simulationTime"
  | "wallClockTime"
  | "sampleIndex";

export type TimeUnit = "s" | "ms" | "us";

export interface TimeoutCondition {
  type: "timeout";
  clock: TimeoutClock;
  value: number;
  unit: TimeUnit;
}

export interface AnyOfCondition {
  type: "anyOf";
  conditions: Condition[];
}

export interface AllOfCondition {
  type: "allOf";
  conditions: Condition[];
}

export interface NotCondition {
  type: "not";
  condition: Condition;
}

export type Condition =
  | ComparisonCondition
  | TimeoutCondition
  | AnyOfCondition
  | AllOfCondition
  | NotCondition;

// --------------------------------------------------------------------------
// Action
// --------------------------------------------------------------------------

export type ActionType =
  | "setBackendInput"
  | "setInternalSignal"
  | "callExternalProcessor";

export interface Action {
  action: ActionType;
  signal?: string;
  value?: string | number | boolean | null;
  processor?: string;
  applyTiming?: string;
}

// --------------------------------------------------------------------------
// Node / Edge
// --------------------------------------------------------------------------

export type NodeType = "start" | "block" | "end" | "condition" | "timer" | "action";

export type ResultValue = "PASS" | "FAIL" | "NOT_EVALUATED";

export interface NodeUI {
  x: number;
  y: number;
  label?: string;
}

export interface DSLNode {
  id: string;
  type: NodeType;
  description?: string;
  entryActions?: Action[];
  ui?: NodeUI;
}

export interface DSLEdge {
  id: string;
  source: string;
  target: string;
  condition?: Condition;
  result?: ResultValue;
  priority?: number;
  actions?: Action[];
}

// --------------------------------------------------------------------------
// Evaluation / Flow / Document
// --------------------------------------------------------------------------

export type AggregationPolicy =
  | "failIfAnyBlockFails"
  | "passIfAllBlocksPass";

export interface Evaluation {
  enabled: boolean;
  aggregation?: AggregationPolicy;
}

export interface DSLFlow {
  id: string;
  name: string;
  description?: string;
  startNodeId: string;
  nodes: DSLNode[];
  edges: DSLEdge[];
  evaluation?: Evaluation;
}

export interface DSLDocument {
  dslVersion: string;
  flows: DSLFlow[];
}

// --------------------------------------------------------------------------
// Validation issue
// --------------------------------------------------------------------------

export interface ValidationIssue {
  level: "error" | "warning";
  code: string;
  message: string;
  flowId?: string;
  nodeId?: string;
  edgeId?: string;
}
