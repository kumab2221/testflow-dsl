from __future__ import annotations

from core.ir.models import (
    AllOfCondition,
    AnyOfCondition,
    ComparisonCondition,
    Condition,
    EdgeIR,
    NotCondition,
    DSLFlowIR,
    TimeoutCondition,
)
from core.semantic_validator.validator import ValidationIssue

_VALID_OPERATORS = frozenset({
    "equals", "notEquals",
    "greaterThan", "greaterThanOrEqual",
    "lessThan", "lessThanOrEqual",
    "risingEdge", "fallingEdge",
})
_VALID_CLOCKS = frozenset({
    "elapsedBlockSimulationTime", "simulationTime", "wallClockTime", "sampleIndex",
})
_VALID_TIME_UNITS = frozenset({"s", "ms", "sample"})
_VALID_RESULTS = frozenset({"PASS", "FAIL", "SKIP", "ERROR", "NOT_EVALUATED"})


class TypeChecker:
    def check(self, ir: DSLFlowIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for flow in ir.flows:
            for edge in flow.edges:
                issues.extend(self._check_edge(flow.id, edge))
        return issues

    def _check_edge(self, flow_id: str, edge: EdgeIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if edge.result and edge.result not in _VALID_RESULTS:
            issues.append(ValidationIssue(
                "error", "INVALID_RESULT",
                f"Invalid result '{edge.result}'",
                flow_id=flow_id, edge_id=edge.id,
            ))
        if edge.condition is not None:
            issues.extend(self._check_condition(flow_id, edge.id, edge.condition))
        return issues

    def _check_condition(self, flow_id: str, edge_id: str, cond: Condition) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if isinstance(cond, ComparisonCondition):
            if cond.operator not in _VALID_OPERATORS:
                issues.append(ValidationIssue(
                    "error", "INVALID_OPERATOR",
                    f"Invalid operator '{cond.operator}'",
                    flow_id=flow_id, edge_id=edge_id,
                ))
        elif isinstance(cond, TimeoutCondition):
            if cond.clock not in _VALID_CLOCKS:
                issues.append(ValidationIssue(
                    "error", "INVALID_CLOCK",
                    f"Invalid clock '{cond.clock}'",
                    flow_id=flow_id, edge_id=edge_id,
                ))
            if cond.unit not in _VALID_TIME_UNITS:
                issues.append(ValidationIssue(
                    "error", "INVALID_UNIT",
                    f"Invalid unit '{cond.unit}'",
                    flow_id=flow_id, edge_id=edge_id,
                ))
        elif isinstance(cond, (AnyOfCondition, AllOfCondition)):
            for c in cond.conditions:
                issues.extend(self._check_condition(flow_id, edge_id, c))
        elif isinstance(cond, NotCondition):
            issues.extend(self._check_condition(flow_id, edge_id, cond.condition))
        return issues
