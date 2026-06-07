from __future__ import annotations

from dataclasses import dataclass

from core.ir.models import FlowIR, NodeIR, DSLFlowIR


@dataclass
class ValidationIssue:
    level: str   # "error" | "warning"
    code: str
    message: str
    flow_id: str = ""
    node_id: str = ""
    edge_id: str = ""

    def __str__(self) -> str:
        loc = f"[flow={self.flow_id}]"
        if self.node_id:
            loc += f"[node={self.node_id}]"
        if self.edge_id:
            loc += f"[edge={self.edge_id}]"
        return f"{self.level.upper()} {self.code} {loc}: {self.message}"


class SemanticValidator:
    def validate(self, ir: DSLFlowIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for flow in ir.flows:
            issues.extend(self._validate_flow(flow))
        return issues

    # ------------------------------------------------------------------

    def _validate_flow(self, flow: FlowIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        issues.extend(self._check_duplicate_ids([n.id for n in flow.nodes], "NODE_ID", flow.id))
        issues.extend(self._check_duplicate_ids([e.id for e in flow.edges], "EDGE_ID", flow.id))

        node_ids = {n.id for n in flow.nodes}

        issues.extend(self._check_start_end(flow))
        issues.extend(self._check_edge_refs(flow, node_ids))

        if not any(i.level == "error" for i in issues):
            issues.extend(self._check_reachability(flow))
            issues.extend(self._check_cycles(flow))

        return issues

    def _check_duplicate_ids(self, ids: list[str], code: str, flow_id: str) -> list[ValidationIssue]:
        seen: set[str] = set()
        issues: list[ValidationIssue] = []
        for id_ in ids:
            if id_ in seen:
                issues.append(ValidationIssue(
                    "error", f"DUPLICATE_{code}",
                    f"Duplicate {code.lower().replace('_', '.')} '{id_}'",
                    flow_id=flow_id,
                ))
            seen.add(id_)
        return issues

    def _check_start_end(self, flow: FlowIR) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        starts = [n for n in flow.nodes if n.type == "start"]
        ends = [n for n in flow.nodes if n.type == "end"]

        if not starts:
            issues.append(ValidationIssue("error", "NO_START_NODE", "Flow has no start node", flow_id=flow.id))
        elif len(starts) > 1:
            issues.append(ValidationIssue("error", "MULTIPLE_START_NODES", "Flow has multiple start nodes", flow_id=flow.id))

        if not ends:
            issues.append(ValidationIssue("error", "NO_END_NODE", "Flow has no end node", flow_id=flow.id))

        return issues

    def _check_edge_refs(self, flow: FlowIR, node_ids: set[str]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for edge in flow.edges:
            if edge.source not in node_ids:
                issues.append(ValidationIssue(
                    "error", "INVALID_EDGE_SOURCE",
                    f"Edge source '{edge.source}' does not exist",
                    flow_id=flow.id, edge_id=edge.id,
                ))
            if edge.target not in node_ids:
                issues.append(ValidationIssue(
                    "error", "INVALID_EDGE_TARGET",
                    f"Edge target '{edge.target}' does not exist",
                    flow_id=flow.id, edge_id=edge.id,
                ))
        return issues

    def _build_adjacency(self, flow: FlowIR) -> dict[str, list[str]]:
        adj: dict[str, list[str]] = {n.id: [] for n in flow.nodes}
        for edge in flow.edges:
            if edge.source in adj:
                adj[edge.source].append(edge.target)
        return adj

    def _check_reachability(self, flow: FlowIR) -> list[ValidationIssue]:
        starts = [n for n in flow.nodes if n.type == "start"]
        if not starts:
            return []

        adj = self._build_adjacency(flow)
        reachable: set[str] = set()
        stack = [starts[0].id]
        while stack:
            nid = stack.pop()
            if nid in reachable:
                continue
            reachable.add(nid)
            stack.extend(adj.get(nid, []))

        return [
            ValidationIssue(
                "warning", "UNREACHABLE_NODE",
                f"Node '{n.id}' is unreachable",
                flow_id=flow.id, node_id=n.id,
            )
            for n in flow.nodes if n.id not in reachable
        ]

    def _check_cycles(self, flow: FlowIR) -> list[ValidationIssue]:
        adj = self._build_adjacency(flow)
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(nid: str) -> bool:
            visited.add(nid)
            rec_stack.add(nid)
            for neighbor in adj.get(nid, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(nid)
            return False

        for node in flow.nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return [ValidationIssue(
                        "warning", "POSSIBLE_CYCLE",
                        "Flow may contain a cycle (possible infinite loop)",
                        flow_id=flow.id,
                    )]
        return []
