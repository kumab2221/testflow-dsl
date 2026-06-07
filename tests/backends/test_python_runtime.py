from pathlib import Path

import pytest

from core.parser import DSLParser
from backends.python_runtime import PythonRuntimeBackend, ResultLog
from backends.python_runtime.capabilities import BackendCapabilities
from backends.python_runtime.clock import SimulationClock
from backends.python_runtime.condition_eval import ConditionEvaluator
from backends.python_runtime.signal_store import SignalStore
from core.ir.models import (
    ComparisonCondition,
    TimeoutCondition,
    AnyOfCondition,
    AllOfCondition,
    NotCondition,
    SignalOperand,
    ValueOperand,
)

EXAMPLES = Path(__file__).parent.parent.parent / "examples"


def make_backend() -> PythonRuntimeBackend:
    return PythonRuntimeBackend()


def parse_and_compile(path: Path = EXAMPLES / "simple_speed_flow.json"):
    parser = DSLParser()
    ir = parser.parse(path)
    backend = make_backend()
    return backend, backend.compile(ir)


# ------------------------------------------------------------------
# Capabilities
# ------------------------------------------------------------------

class TestCapabilities:
    def test_get_capabilities_returns_dataclass(self):
        caps = make_backend().get_capabilities()
        assert isinstance(caps, BackendCapabilities)
        assert caps.backend == "python-runtime"

    def test_sequence_supported(self):
        assert make_backend().get_capabilities().sequence is True

    def test_parallel_not_supported(self):
        assert make_backend().get_capabilities().parallel is False

    def test_validate_valid_ir(self):
        parser = DSLParser()
        ir = parser.parse(EXAMPLES / "simple_speed_flow.json")
        issues = make_backend().validate_capabilities(ir)
        assert issues == []


# ------------------------------------------------------------------
# End-to-end: simple_speed_flow.json
# ------------------------------------------------------------------

class TestSimpleSpeedFlow:
    def test_pass_when_speed_exceeds_100(self):
        backend, plan = parse_and_compile()
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 120.0})
        assert result.flows[0].flow_result == "PASS"
        assert result.flows[0].blocks[0].result == "PASS"

    def test_fail_when_speed_never_reaches_100(self):
        backend, plan = parse_and_compile()
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 50.0}, tick_size=1.0)
        assert result.flows[0].flow_result == "FAIL"
        assert result.flows[0].blocks[0].result == "FAIL"

    def test_result_log_has_exited_edge_id(self):
        backend, plan = parse_and_compile()
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 120.0})
        block = result.flows[0].blocks[0]
        assert block.exited_edge_id is not None

    def test_evaluation_disabled_returns_not_evaluated(self):
        parser = DSLParser()
        ir = parser.parse(EXAMPLES / "simple_speed_flow.json")
        # evaluation.enabled=False に書き換えて検証
        ir.flows[0].evaluation.enabled = False
        backend = make_backend()
        plan = backend.compile(ir)
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 120.0})
        assert result.flows[0].flow_result == "NOT_EVALUATED"
        assert result.flows[0].blocks[0].result == "NOT_EVALUATED"

    def test_result_log_type(self):
        backend, plan = parse_and_compile()
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 120.0})
        assert isinstance(result, ResultLog)
        assert result.backend == "python-runtime"

    def test_print_summary_runs_without_error(self, capsys):
        backend, plan = parse_and_compile()
        result = backend.run(plan, signal_provider=lambda t: {"vehicleSpeed": 120.0})
        result.print_summary()
        captured = capsys.readouterr()
        assert "PASS" in captured.out


# ------------------------------------------------------------------
# ConditionEvaluator
# ------------------------------------------------------------------

class TestConditionEvaluator:
    def setup_method(self):
        self.ev = ConditionEvaluator()
        self.store = SignalStore({"speed": 120.0})
        self.clock = SimulationClock()

    def _cmp(self, op: str, left_val=None, right_val=100.0):
        left = SignalOperand("observed", "speed") if left_val is None else ValueOperand(left_val)
        return ComparisonCondition(left=left, operator=op, right=ValueOperand(right_val))

    def test_comparison_gte_true(self):
        cond = self._cmp("greaterThanOrEqual")
        assert self.ev.evaluate(cond, self.store, self.clock) is True

    def test_comparison_gte_false(self):
        store = SignalStore({"speed": 50.0})
        cond = self._cmp("greaterThanOrEqual")
        assert self.ev.evaluate(cond, store, self.clock) is False

    def test_comparison_missing_signal_returns_false(self):
        store = SignalStore()
        cond = self._cmp("greaterThanOrEqual")
        assert self.ev.evaluate(cond, store, self.clock) is False

    def test_timeout_not_yet(self):
        cond = TimeoutCondition(clock="elapsedBlockSimulationTime", value=60.0, unit="s")
        assert self.ev.evaluate(cond, self.store, self.clock) is False

    def test_timeout_elapsed(self):
        cond = TimeoutCondition(clock="elapsedBlockSimulationTime", value=60.0, unit="s")
        self.clock.start_block()
        for _ in range(60):
            self.clock.tick(1.0)
        assert self.ev.evaluate(cond, self.store, self.clock) is True

    def test_anyof_true_when_one_true(self):
        cond = AnyOfCondition(conditions=[
            self._cmp("greaterThanOrEqual"),                     # True
            TimeoutCondition("elapsedBlockSimulationTime", 60.0, "s"),  # False
        ])
        assert self.ev.evaluate(cond, self.store, self.clock) is True

    def test_allof_false_when_one_false(self):
        cond = AllOfCondition(conditions=[
            self._cmp("greaterThanOrEqual"),                     # True
            TimeoutCondition("elapsedBlockSimulationTime", 60.0, "s"),  # False
        ])
        assert self.ev.evaluate(cond, self.store, self.clock) is False

    def test_not_inverts(self):
        cond = NotCondition(condition=self._cmp("greaterThanOrEqual"))
        assert self.ev.evaluate(cond, self.store, self.clock) is False

    def test_all_comparison_operators(self):
        cases = [
            ("equals", 100.0, 100.0, True),
            ("notEquals", 100.0, 99.0, True),
            ("greaterThan", 101.0, 100.0, True),
            ("lessThan", 99.0, 100.0, True),
            ("lessThanOrEqual", 100.0, 100.0, True),
        ]
        for op, left_v, right_v, expected in cases:
            cond = ComparisonCondition(
                left=ValueOperand(left_v), operator=op, right=ValueOperand(right_v)
            )
            result = self.ev.evaluate(cond, self.store, self.clock)
            assert result is expected, f"operator={op}"
