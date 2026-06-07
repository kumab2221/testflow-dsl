from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BlockResult:
    node_id: str
    result: str          # PASS | FAIL | SKIP | ERROR | NOT_EVALUATED
    exited_edge_id: str | None = None


@dataclass
class FlowResult:
    flow_id: str
    flow_result: str     # PASS | FAIL | NOT_EVALUATED
    blocks: list[BlockResult] = field(default_factory=list)


@dataclass
class ResultLog:
    backend: str
    flows: list[FlowResult] = field(default_factory=list)

    def print_summary(self) -> None:
        print(f"[{self.backend}]")
        for flow in self.flows:
            print(f"  Flow {flow.flow_id}: {flow.flow_result}")
            for block in flow.blocks:
                edge_info = f" (edge={block.exited_edge_id})" if block.exited_edge_id else ""
                print(f"    Block {block.node_id}: {block.result}{edge_info}")
