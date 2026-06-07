from pathlib import Path

import pytest

from core.parser import DSLParser, ParseError
from core.ir.models import ComparisonCondition, TimeoutCondition, SignalOperand, ValueOperand

EXAMPLES = Path(__file__).parent.parent.parent / "examples"


def make_parser() -> DSLParser:
    return DSLParser()


def minimal_dsl(**overrides) -> dict:
    base = {
        "dslVersion": "0.1.0",
        "flows": [
            {
                "id": "FLOW-001",
                "name": "Test",
                "nodes": [
                    {"id": "START", "type": "start"},
                    {"id": "END", "type": "end"},
                ],
                "edges": [{"id": "E1", "source": "START", "target": "END"}],
            }
        ],
    }
    base.update(overrides)
    return base


class TestDSLParser:
    def test_parse_simple_speed_flow(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        assert ir.ir_version == "0.1.0"
        assert len(ir.flows) == 1

    def test_flow_fields(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        flow = ir.flows[0]
        assert flow.id == "FLOW-001"
        assert flow.name == "Vehicle speed test"
        assert flow.start_node_id == "START"

    def test_nodes_parsed(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        flow = ir.flows[0]
        types = {n.type for n in flow.nodes}
        assert "start" in types
        assert "block" in types
        assert "end" in types

    def test_block_description(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        block = next(n for n in ir.flows[0].nodes if n.type == "block")
        assert "100km/h" in block.description

    def test_comparison_condition(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        edges = ir.flows[0].edges
        pass_edge = next(e for e in edges if e.result == "PASS")
        assert isinstance(pass_edge.condition, ComparisonCondition)
        assert isinstance(pass_edge.condition.left, SignalOperand)
        assert pass_edge.condition.left.signal == "vehicleSpeed"
        assert isinstance(pass_edge.condition.right, ValueOperand)
        assert pass_edge.condition.right.value == 100.0

    def test_timeout_condition(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        edges = ir.flows[0].edges
        fail_edge = next(e for e in edges if e.result == "FAIL")
        assert isinstance(fail_edge.condition, TimeoutCondition)
        assert fail_edge.condition.clock == "elapsedBlockSimulationTime"
        assert fail_edge.condition.value == 60.0

    def test_evaluation_parsed(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        ev = ir.flows[0].evaluation
        assert ev is not None
        assert ev.enabled is True
        assert ev.aggregation == "failIfAnyBlockFails"

    def test_edge_priority(self):
        ir = make_parser().parse(EXAMPLES / "simple_speed_flow.json")
        edges = {e.result: e for e in ir.flows[0].edges if e.result}
        assert edges["PASS"].priority == 1
        assert edges["FAIL"].priority == 2

    def test_schema_error_raises_parse_error(self):
        bad = minimal_dsl(dslVersion="bad-version")
        with pytest.raises(ParseError, match="Schema validation failed"):
            make_parser().parse_dict(bad)

    def test_missing_required_field_raises(self):
        bad = {"dslVersion": "0.1.0"}
        with pytest.raises(ParseError):
            make_parser().parse_dict(bad)

    def test_minimal_dsl_parses(self):
        ir = make_parser().parse_dict(minimal_dsl())
        assert len(ir.flows) == 1
        assert ir.flows[0].start_node_id == "START"
