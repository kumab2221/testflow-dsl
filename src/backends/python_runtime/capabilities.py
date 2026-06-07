from __future__ import annotations

from dataclasses import dataclass, field

from core.ir.models import DSLFlowIR


@dataclass
class BackendCapabilities:
    backend: str
    version: str
    sequence: bool = True
    parallel: bool = False
    nested_parallel: bool = False
    comparison_condition: bool = True
    timeout_condition: bool = True
    simulation_time: bool = True
    runtime_feedback: bool = False
    external_processor: bool = False


@dataclass
class CompiledPlan:
    ir: DSLFlowIR
    backend: str
