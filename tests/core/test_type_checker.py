from core.ir.models import (
    ComparisonCondition,
    EdgeIR,
    FlowIR,
    NodeIR,
    SignalOperand,
    DSLFlowIR,
    TimeoutCondition,
    ValueOperand,
)
from core.type_checker import TypeChecker


def make_ir(edges: list[EdgeIR]) -> DSLFlowIR:
    return DSLFlowIR(
        ir_version="0.1.0",
        flows=[
            FlowIR(
                id="FLOW-001",
                name="Test",
                start_node_id="START",
                nodes=[NodeIR(id="START", type="start"), NodeIR(id="END", type="end")],
                edges=edges,
            )
        ],
    )


def comparison_edge(operator: str, result: str = "PASS") -> EdgeIR:
    return EdgeIR(
        id="E1",
        source="START",
        target="END",
        condition=ComparisonCondition(
            left=SignalOperand(source="observed", signal="speed"),
            operator=operator,
            right=ValueOperand(value=100.0),
        ),
        result=result,
    )


def timeout_edge(clock: str, unit: str) -> EdgeIR:
    return EdgeIR(
        id="E1",
        source="START",
        target="END",
        condition=TimeoutCondition(clock=clock, value=60.0, unit=unit),
    )


def codes(issues) -> set[str]:
    return {i.code for i in issues}


class TestTypeChecker:
    def setup_method(self):
        self.tc = TypeChecker()

    def test_valid_comparison_no_issues(self):
        issues = self.tc.check(make_ir([comparison_edge("greaterThanOrEqual")]))
        assert issues == []

    def test_valid_timeout_no_issues(self):
        issues = self.tc.check(make_ir([timeout_edge("elapsedBlockSimulationTime", "s")]))
        assert issues == []

    def test_invalid_operator(self):
        issues = self.tc.check(make_ir([comparison_edge("badOperator")]))
        assert "INVALID_OPERATOR" in codes(issues)

    def test_invalid_clock(self):
        issues = self.tc.check(make_ir([timeout_edge("badClock", "s")]))
        assert "INVALID_CLOCK" in codes(issues)

    def test_invalid_unit(self):
        issues = self.tc.check(make_ir([timeout_edge("simulationTime", "min")]))
        assert "INVALID_UNIT" in codes(issues)

    def test_invalid_result(self):
        issues = self.tc.check(make_ir([comparison_edge("equals", result="UNKNOWN")]))
        assert "INVALID_RESULT" in codes(issues)

    def test_all_valid_operators(self):
        valid = ["equals", "notEquals", "greaterThan", "greaterThanOrEqual",
                 "lessThan", "lessThanOrEqual", "risingEdge", "fallingEdge"]
        for op in valid:
            issues = self.tc.check(make_ir([comparison_edge(op)]))
            assert issues == [], f"Operator '{op}' should be valid"

    def test_all_valid_clocks(self):
        for clock in ["elapsedBlockSimulationTime", "simulationTime", "wallClockTime", "sampleIndex"]:
            issues = self.tc.check(make_ir([timeout_edge(clock, "s")]))
            assert issues == [], f"Clock '{clock}' should be valid"
