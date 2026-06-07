from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.ir.models import (
    ActionIR,
    AllOfCondition,
    AnyOfCondition,
    ComparisonCondition,
    Condition,
    EdgeIR,
    EvaluationIR,
    FlowIR,
    NodeIR,
    NotCondition,
    Operand,
    SignalOperand,
    DSLFlowIR,
    TimeoutCondition,
    ValueOperand,
)

_DEFAULT_SCHEMA = Path(__file__).parent.parent.parent.parent / "schemas" / "testflow-dsl.schema.json"

IR_VERSION = "0.1.0"


class ParseError(Exception):
    pass


class DSLParser:
    def __init__(self, schema_path: Path = _DEFAULT_SCHEMA) -> None:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        self._validator = validator_cls(schema)

    def parse(self, dsl_path: Path) -> DSLFlowIR:
        raw = json.loads(dsl_path.read_text(encoding="utf-8"))
        self._validate_schema(raw, dsl_path)
        return self._build_ir(raw)

    def parse_dict(self, data: dict) -> DSLFlowIR:
        self._validate_schema(data, "<dict>")
        return self._build_ir(data)

    # ------------------------------------------------------------------

    def _validate_schema(self, data: dict, source: object) -> None:
        errors = sorted(self._validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            lines = [f"  {'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]
            raise ParseError(f"Schema validation failed for {source}:\n" + "\n".join(lines))

    def _build_ir(self, data: dict) -> DSLFlowIR:
        return DSLFlowIR(
            ir_version=IR_VERSION,
            flows=[self._build_flow(f) for f in data["flows"]],
        )

    def _build_flow(self, data: dict) -> FlowIR:
        nodes = [self._build_node(n) for n in data["nodes"]]
        start_nodes = [n for n in nodes if n.type == "start"]
        start_node_id = start_nodes[0].id if start_nodes else ""

        evaluation: EvaluationIR | None = None
        if "evaluation" in data:
            e = data["evaluation"]
            evaluation = EvaluationIR(enabled=e["enabled"], aggregation=e.get("aggregation"))

        return FlowIR(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            start_node_id=start_node_id,
            nodes=nodes,
            edges=[self._build_edge(e) for e in data["edges"]],
            evaluation=evaluation,
        )

    def _build_node(self, data: dict) -> NodeIR:
        return NodeIR(
            id=data["id"],
            type=data["type"],
            description=data.get("data", {}).get("description", ""),
        )

    def _build_edge(self, data: dict) -> EdgeIR:
        return EdgeIR(
            id=data["id"],
            source=data["source"],
            target=data["target"],
            condition=self._build_condition(data["condition"]) if "condition" in data else None,
            result=data.get("result"),
            priority=data.get("priority", 0),
            actions=[self._build_action(a) for a in data.get("actions", [])],
        )

    def _build_condition(self, data: dict) -> Condition:
        t = data["type"]
        if t == "comparison":
            return ComparisonCondition(
                left=self._build_operand(data["left"]),
                operator=data["operator"],
                right=self._build_operand(data["right"]),
                unit=data.get("unit"),
            )
        if t == "timeout":
            return TimeoutCondition(clock=data["clock"], value=data["value"], unit=data["unit"])
        if t == "anyOf":
            return AnyOfCondition(conditions=[self._build_condition(c) for c in data["anyOf"]])
        if t == "allOf":
            return AllOfCondition(conditions=[self._build_condition(c) for c in data["allOf"]])
        if t == "not":
            return NotCondition(condition=self._build_condition(data["not"]))
        raise ParseError(f"Unknown condition type: {t!r}")

    def _build_operand(self, data: dict) -> Operand:
        if "signal" in data:
            return SignalOperand(source=data["source"], signal=data["signal"])
        return ValueOperand(value=data["value"])

    def _build_action(self, data: dict) -> ActionIR:
        return ActionIR(
            action=data["action"],
            signal=data.get("signal"),
            value=data.get("value"),
            processor=data.get("processor"),
            apply_timing=data.get("applyTiming"),
        )
