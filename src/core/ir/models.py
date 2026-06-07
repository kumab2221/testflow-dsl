from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SignalOperand:
    source: str  # "backendInput" | "observed" | "internal" | "derived" | "reference" | "clock"
    signal: str


@dataclass
class ValueOperand:
    value: str | int | float | bool | None


Operand = SignalOperand | ValueOperand


@dataclass
class ComparisonCondition:
    left: Operand
    operator: str
    right: Operand
    unit: str | None = None


@dataclass
class TimeoutCondition:
    clock: str
    value: float
    unit: str


@dataclass
class AnyOfCondition:
    conditions: list[Condition]


@dataclass
class AllOfCondition:
    conditions: list[Condition]


@dataclass
class NotCondition:
    condition: Condition


Condition = ComparisonCondition | TimeoutCondition | AnyOfCondition | AllOfCondition | NotCondition


@dataclass
class ActionIR:
    action: str  # "setBackendInput" | "setInternalSignal" | "callExternalProcessor"
    signal: str | None = None
    value: str | int | float | bool | None = None
    processor: str | None = None
    apply_timing: str | None = None


@dataclass
class NodeIR:
    id: str
    type: str  # "start" | "end" | "block" | "action" | "condition" | "timer"
    description: str = ""
    entry_actions: list[ActionIR] = field(default_factory=list)


@dataclass
class EdgeIR:
    id: str
    source: str
    target: str
    condition: Condition | None = None
    result: str | None = None
    priority: int = 0
    actions: list[ActionIR] = field(default_factory=list)


@dataclass
class EvaluationIR:
    enabled: bool
    aggregation: str | None = None


@dataclass
class FlowIR:
    id: str
    name: str
    start_node_id: str
    nodes: list[NodeIR]
    edges: list[EdgeIR]
    description: str = ""
    evaluation: EvaluationIR | None = None


@dataclass
class DSLFlowIR:
    ir_version: str
    flows: list[FlowIR]
