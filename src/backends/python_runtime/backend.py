from __future__ import annotations

from typing import Any, Callable

from core.ir.models import DSLFlowIR
from core.semantic_validator.validator import ValidationIssue

from backends.python_runtime.capabilities import BackendCapabilities, CompiledPlan
from backends.python_runtime.executor import FlowExecutor, SignalProvider
from backends.python_runtime.result_log import ResultLog

_BACKEND_ID = "python-runtime"
_VERSION = "0.1.0"

_UNSUPPORTED_NODE_TYPES = frozenset({"parallel", "sequence", "join"})


class PythonRuntimeBackend:
    """Python で動作する最小バックエンド。v0.1 は逐次フローのみ対応。"""

    def get_capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            backend=_BACKEND_ID,
            version=_VERSION,
            sequence=True,
            parallel=False,
            nested_parallel=False,
            comparison_condition=True,
            timeout_condition=True,
            simulation_time=True,
            runtime_feedback=False,
            external_processor=False,
        )

    def validate_capabilities(self, ir: DSLFlowIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for flow in ir.flows:
            for node in flow.nodes:
                if node.type in _UNSUPPORTED_NODE_TYPES:
                    issues.append(ValidationIssue(
                        "error", "UNSUPPORTED_NODE_TYPE",
                        f"Node type '{node.type}' is not supported by {_BACKEND_ID}",
                        flow_id=flow.id, node_id=node.id,
                    ))
        return issues

    def compile(self, ir: DSLFlowIR) -> CompiledPlan:
        issues = [i for i in self.validate_capabilities(ir) if i.level == "error"]
        if issues:
            details = "\n".join(str(i) for i in issues)
            raise RuntimeError(f"Capability validation failed:\n{details}")
        return CompiledPlan(ir=ir, backend=_BACKEND_ID)

    def run(
        self,
        plan: CompiledPlan,
        signal_provider: SignalProvider | None = None,
        tick_size: float = 1.0,
    ) -> ResultLog:
        executor = FlowExecutor(tick_size=tick_size)
        flow_results = [executor.execute(flow, signal_provider) for flow in plan.ir.flows]
        return ResultLog(backend=_BACKEND_ID, flows=flow_results)
