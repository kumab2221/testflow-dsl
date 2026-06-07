from __future__ import annotations

import logging
from typing import Any, Callable

from core.ir.models import EdgeIR, FlowIR, NodeIR

from backends.python_runtime.clock import SimulationClock
from backends.python_runtime.condition_eval import ConditionEvaluator
from backends.python_runtime.result_log import BlockResult, FlowResult
from backends.python_runtime.signal_store import SignalStore

logger = logging.getLogger(__name__)

SignalProvider = Callable[[float], dict[str, Any]]

_MAX_STEPS = 100_000
_PASSTHROUGH_TYPES = frozenset({"start", "action", "condition", "timer"})


class FlowExecutor:
    """単一 FlowIR を逐次実行する。並列は v0.2 以降。"""

    def __init__(self, tick_size: float = 1.0) -> None:
        self._tick = tick_size
        self._evaluator = ConditionEvaluator()

    def execute(
        self,
        flow: FlowIR,
        signal_provider: SignalProvider | None = None,
    ) -> FlowResult:
        store = SignalStore()
        clock = SimulationClock()
        blocks: list[BlockResult] = []

        node_index = {n.id: n for n in flow.nodes}
        current_id = flow.start_node_id

        for _ in range(_MAX_STEPS):
            node = node_index[current_id]
            logger.debug("entering node %s (type=%s)", node.id, node.type)

            if node.type == "end":
                break

            if node.type in _PASSTHROUGH_TYPES:
                edge = self._find_unconditional(flow, current_id)
                if edge is None:
                    logger.warning("no outgoing edge from node %s", current_id)
                    break
                current_id = edge.target
                continue

            if node.type == "block":
                clock.start_block()
                fired_edge, raw_result = self._run_block(node, flow, store, clock, signal_provider)

                effective = (
                    "NOT_EVALUATED"
                    if (flow.evaluation and not flow.evaluation.enabled)
                    else raw_result
                )
                blocks.append(BlockResult(
                    node_id=node.id,
                    result=effective,
                    exited_edge_id=fired_edge.id if fired_edge else None,
                ))
                logger.info("block %s → %s", node.id, effective)

                if fired_edge:
                    current_id = fired_edge.target
                else:
                    break
                continue

            logger.warning("unhandled node type %r at %s", node.type, node.id)
            break

        flow_result = self._aggregate(flow, blocks)
        logger.info("flow %s → %s", flow.id, flow_result)
        return FlowResult(flow_id=flow.id, flow_result=flow_result, blocks=blocks)

    # ------------------------------------------------------------------

    def _run_block(
        self,
        node: NodeIR,
        flow: FlowIR,
        store: SignalStore,
        clock: SimulationClock,
        signal_provider: SignalProvider | None,
    ) -> tuple[EdgeIR | None, str]:
        outgoing = sorted(
            [e for e in flow.edges if e.source == node.id],
            key=lambda e: e.priority,
        )

        for _ in range(_MAX_STEPS):
            if signal_provider:
                store.update(signal_provider(clock.simulation_time()))

            for edge in outgoing:
                if edge.condition is None:
                    return edge, edge.result or "NOT_EVALUATED"
                if self._evaluator.evaluate(edge.condition, store, clock):
                    return edge, edge.result or "NOT_EVALUATED"

            clock.tick(self._tick)

        logger.error("block %s exceeded max steps", node.id)
        return None, "ERROR"

    def _find_unconditional(self, flow: FlowIR, node_id: str) -> EdgeIR | None:
        for edge in flow.edges:
            if edge.source == node_id and edge.condition is None:
                return edge
        return None

    def _aggregate(self, flow: FlowIR, blocks: list[BlockResult]) -> str:
        if not flow.evaluation or not flow.evaluation.enabled:
            return "NOT_EVALUATED"
        if not blocks:
            return "NOT_EVALUATED"

        results = [b.result for b in blocks]
        match flow.evaluation.aggregation:
            case "failIfAnyBlockFails":
                return "FAIL" if "FAIL" in results else "PASS"
            case "passIfAllBlocksPass":
                return "PASS" if all(r == "PASS" for r in results) else "FAIL"
            case _:
                return "NOT_EVALUATED"
