from __future__ import annotations

from typing import Any

from core.ir.models import (
    AllOfCondition,
    AnyOfCondition,
    ComparisonCondition,
    Condition,
    NotCondition,
    SignalOperand,
    TimeoutCondition,
    ValueOperand,
)
from backends.python_runtime.clock import SimulationClock
from backends.python_runtime.signal_store import SignalStore


class ConditionEvaluator:
    """Condition を SignalStore / SimulationClock を使って評価する。"""

    def evaluate(self, cond: Condition, store: SignalStore, clock: SimulationClock) -> bool:
        if isinstance(cond, ComparisonCondition):
            return self._eval_comparison(cond, store)
        if isinstance(cond, TimeoutCondition):
            return self._eval_timeout(cond, clock)
        if isinstance(cond, AnyOfCondition):
            return any(self.evaluate(c, store, clock) for c in cond.conditions)
        if isinstance(cond, AllOfCondition):
            return all(self.evaluate(c, store, clock) for c in cond.conditions)
        if isinstance(cond, NotCondition):
            return not self.evaluate(cond.condition, store, clock)
        raise TypeError(f"Unknown condition type: {type(cond)}")

    def _eval_comparison(self, cond: ComparisonCondition, store: SignalStore) -> bool:
        left = self._resolve(cond.left, store)
        right = self._resolve(cond.right, store)
        if left is None or right is None:
            return False
        return self._apply_operator(cond.operator, left, right)

    def _eval_timeout(self, cond: TimeoutCondition, clock: SimulationClock) -> bool:
        match cond.clock:
            case "elapsedBlockSimulationTime":
                return clock.elapsed_block_time() >= cond.value
            case "simulationTime":
                return clock.simulation_time() >= cond.value
            case _:
                return False  # wallClockTime / sampleIndex は v0.1 では未対応

    def _resolve(self, operand: Any, store: SignalStore) -> Any:
        if isinstance(operand, SignalOperand):
            return store.get(operand.signal)
        if isinstance(operand, ValueOperand):
            return operand.value
        return None

    def _apply_operator(self, op: str, left: Any, right: Any) -> bool:
        try:
            match op:
                case "equals":             return left == right
                case "notEquals":          return left != right
                case "greaterThan":        return left > right
                case "greaterThanOrEqual": return left >= right
                case "lessThan":           return left < right
                case "lessThanOrEqual":    return left <= right
                case _:                    return False  # risingEdge / fallingEdge は v0.1 では未対応
        except TypeError:
            return False
