import { useState } from "react";
import { useDSL } from "../store/dslStore";
import type { Action, ActionType, DSLEdge, DSLNode, ResultValue } from "../types/dsl";

const ACTION_TYPES: ActionType[] = [
  "setBackendInput",
  "setInternalSignal",
  "callExternalProcessor",
];

const RESULTS: Array<ResultValue | ""> = ["", "PASS", "FAIL", "NOT_EVALUATED"];

function NodeEditor({ node }: { node: DSLNode }) {
  const { dispatch } = useDSL();
  const [desc, setDesc] = useState(node.description ?? "");

  function handleDescBlur() {
    if (desc !== (node.description ?? "")) {
      dispatch({ type: "UPDATE_NODE_DESC", nodeId: node.id, description: desc });
    }
  }

  function handleAddAction(actionType: ActionType) {
    const action: Action = { action: actionType };
    dispatch({ type: "ADD_NODE_ACTION", nodeId: node.id, action });
  }

  return (
    <div>
      <h3 style={{ margin: "0 0 8px" }}>
        Node: {node.id}{" "}
        <span style={{ fontSize: 11, color: "#aaa" }}>({node.type})</span>
      </h3>

      <label style={labelStyle}>description</label>
      <textarea
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        onBlur={handleDescBlur}
        rows={4}
        style={inputStyle}
      />

      <div style={{ marginTop: 12 }}>
        <label style={labelStyle}>
          Entry Actions ({node.entryActions?.length ?? 0})
        </label>
        {node.entryActions?.map((a, i) => (
          <div key={i} style={chipStyle}>
            {a.action}
            {a.signal && <span style={{ color: "#aaa" }}> → {a.signal}</span>}
          </div>
        ))}
        <select
          defaultValue=""
          onChange={(e) => {
            if (e.target.value) {
              handleAddAction(e.target.value as ActionType);
              e.target.value = "";
            }
          }}
          style={{ ...inputStyle, marginTop: 6 }}
        >
          <option value="">+ Add action…</option>
          {ACTION_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

function EdgeEditor({ edge }: { edge: DSLEdge }) {
  const { dispatch } = useDSL();

  function handleResultChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const v = e.target.value;
    dispatch({
      type: "UPDATE_EDGE_RESULT",
      edgeId: edge.id,
      result: v || undefined,
    });
  }

  function handlePriorityChange(e: React.ChangeEvent<HTMLInputElement>) {
    dispatch({
      type: "UPDATE_EDGE_PRIORITY",
      edgeId: edge.id,
      priority: Number(e.target.value),
    });
  }

  const conditionSummary = edge.condition
    ? summarizeCondition(edge.condition)
    : "(none)";

  return (
    <div>
      <h3 style={{ margin: "0 0 8px" }}>Edge: {edge.id}</h3>
      <div style={{ fontSize: 12, color: "#aaa", marginBottom: 12 }}>
        {edge.source} → {edge.target}
      </div>

      <label style={labelStyle}>result</label>
      <select
        value={edge.result ?? ""}
        onChange={handleResultChange}
        style={inputStyle}
      >
        {RESULTS.map((r) => (
          <option key={r} value={r}>
            {r || "(none)"}
          </option>
        ))}
      </select>

      <label style={{ ...labelStyle, marginTop: 10 }}>priority</label>
      <input
        type="number"
        value={edge.priority ?? 0}
        onChange={handlePriorityChange}
        style={inputStyle}
      />

      <label style={{ ...labelStyle, marginTop: 10 }}>condition</label>
      <div style={{ ...chipStyle, color: "#ccc", fontFamily: "monospace", fontSize: 11 }}>
        {conditionSummary}
      </div>
    </div>
  );
}

function summarizeCondition(c: import("../types/dsl").Condition): string {
  switch (c.type) {
    case "comparison": {
      const left =
        "source" in c.left
          ? `${c.left.source}:${c.left.signal}`
          : String(c.value);
      const right =
        "source" in c.right
          ? `${c.right.source}:${c.right.signal}`
          : String((c.right as import("../types/dsl").ValueOperand).value);
      return `${left} ${c.operator} ${right}`;
    }
    case "timeout":
      return `timeout ${c.clock} >= ${c.value}${c.unit}`;
    case "anyOf":
      return `anyOf(${c.conditions.length})`;
    case "allOf":
      return `allOf(${c.conditions.length})`;
    case "not":
      return `not(${summarizeCondition(c.condition)})`;
  }
}

export default function PropertyPanel() {
  const { state } = useDSL();
  if (!state.doc) return <PanelShell>ファイルを開いてください</PanelShell>;

  const flow = state.doc.flows[0];
  if (!flow) return <PanelShell>フローがありません</PanelShell>;

  if (state.selectedNodeId) {
    const node = flow.nodes.find((n) => n.id === state.selectedNodeId);
    if (node) return <PanelShell><NodeEditor node={node} /></PanelShell>;
  }

  if (state.selectedEdgeId) {
    const edge = flow.edges.find((e) => e.id === state.selectedEdgeId);
    if (edge) return <PanelShell><EdgeEditor edge={edge} /></PanelShell>;
  }

  return <PanelShell>(何も選択されていません)</PanelShell>;
}

function PanelShell({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        width: 280,
        background: "#1a1a2e",
        borderLeft: "1px solid #333",
        padding: 16,
        overflowY: "auto",
        color: "#e0e0e0",
        fontSize: 13,
      }}
    >
      {children}
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 11,
  color: "#aaa",
  marginBottom: 4,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  background: "#0d1117",
  border: "1px solid #444",
  borderRadius: 4,
  color: "#e0e0e0",
  padding: "4px 8px",
  fontSize: 13,
  boxSizing: "border-box",
};

const chipStyle: React.CSSProperties = {
  background: "#111827",
  border: "1px solid #333",
  borderRadius: 4,
  padding: "3px 8px",
  marginBottom: 4,
  fontSize: 12,
};
