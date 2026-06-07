import pytest

from core.ir.models import EdgeIR, FlowIR, NodeIR, DSLFlowIR
from core.semantic_validator import SemanticValidator


def make_ir(*flows: FlowIR) -> DSLFlowIR:
    return DSLFlowIR(ir_version="0.1.0", flows=list(flows))


def simple_flow(**overrides) -> FlowIR:
    base = FlowIR(
        id="FLOW-001",
        name="Test",
        start_node_id="START",
        nodes=[
            NodeIR(id="START", type="start"),
            NodeIR(id="BLOCK-001", type="block"),
            NodeIR(id="END", type="end"),
        ],
        edges=[
            EdgeIR(id="E1", source="START", target="BLOCK-001"),
            EdgeIR(id="E2", source="BLOCK-001", target="END"),
        ],
    )
    for k, v in overrides.items():
        object.__setattr__(base, k, v)
    return base


def codes(issues) -> set[str]:
    return {i.code for i in issues}


def errors(issues) -> list:
    return [i for i in issues if i.level == "error"]


def warnings(issues) -> list:
    return [i for i in issues if i.level == "warning"]


class TestSemanticValidator:
    def setup_method(self):
        self.v = SemanticValidator()

    def test_valid_flow_no_issues(self):
        issues = self.v.validate(make_ir(simple_flow()))
        assert errors(issues) == []

    def test_duplicate_node_id(self):
        flow = simple_flow(nodes=[
            NodeIR(id="START", type="start"),
            NodeIR(id="START", type="block"),
            NodeIR(id="END", type="end"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "DUPLICATE_NODE_ID" in codes(errors(issues))

    def test_duplicate_edge_id(self):
        flow = simple_flow(edges=[
            EdgeIR(id="E1", source="START", target="BLOCK-001"),
            EdgeIR(id="E1", source="BLOCK-001", target="END"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "DUPLICATE_EDGE_ID" in codes(errors(issues))

    def test_no_start_node(self):
        flow = simple_flow(nodes=[
            NodeIR(id="BLOCK-001", type="block"),
            NodeIR(id="END", type="end"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "NO_START_NODE" in codes(errors(issues))

    def test_multiple_start_nodes(self):
        flow = simple_flow(nodes=[
            NodeIR(id="START", type="start"),
            NodeIR(id="START2", type="start"),
            NodeIR(id="END", type="end"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "MULTIPLE_START_NODES" in codes(errors(issues))

    def test_no_end_node(self):
        flow = simple_flow(nodes=[
            NodeIR(id="START", type="start"),
            NodeIR(id="BLOCK-001", type="block"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "NO_END_NODE" in codes(errors(issues))

    def test_invalid_edge_source(self):
        flow = simple_flow(edges=[
            EdgeIR(id="E1", source="NONEXISTENT", target="END"),
            EdgeIR(id="E2", source="START", target="END"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "INVALID_EDGE_SOURCE" in codes(errors(issues))

    def test_invalid_edge_target(self):
        flow = simple_flow(edges=[
            EdgeIR(id="E1", source="START", target="NONEXISTENT"),
            EdgeIR(id="E2", source="START", target="END"),
        ])
        issues = self.v.validate(make_ir(flow))
        assert "INVALID_EDGE_TARGET" in codes(errors(issues))

    def test_unreachable_node_warning(self):
        flow = simple_flow(
            nodes=[
                NodeIR(id="START", type="start"),
                NodeIR(id="BLOCK-001", type="block"),
                NodeIR(id="ORPHAN", type="block"),
                NodeIR(id="END", type="end"),
            ],
            edges=[
                EdgeIR(id="E1", source="START", target="BLOCK-001"),
                EdgeIR(id="E2", source="BLOCK-001", target="END"),
            ],
        )
        issues = self.v.validate(make_ir(flow))
        assert errors(issues) == []
        assert "UNREACHABLE_NODE" in codes(warnings(issues))

    def test_cycle_warning(self):
        flow = simple_flow(
            nodes=[
                NodeIR(id="START", type="start"),
                NodeIR(id="A", type="block"),
                NodeIR(id="B", type="block"),
                NodeIR(id="END", type="end"),
            ],
            edges=[
                EdgeIR(id="E1", source="START", target="A"),
                EdgeIR(id="E2", source="A", target="B"),
                EdgeIR(id="E3", source="B", target="A"),
                EdgeIR(id="E4", source="B", target="END"),
            ],
        )
        issues = self.v.validate(make_ir(flow))
        assert errors(issues) == []
        assert "POSSIBLE_CYCLE" in codes(warnings(issues))
