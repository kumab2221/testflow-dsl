import { useDSL } from "../store/dslStore";

export default function ValidationPanel() {
  const { state } = useDSL();
  const issues = state.issues;

  if (issues.length === 0) {
    return (
      <div style={panelStyle}>
        <span style={{ color: "#4caf50" }}>✓ No issues</span>
      </div>
    );
  }

  return (
    <div style={panelStyle}>
      {issues.map((issue, i) => (
        <div
          key={i}
          style={{
            ...issueStyle,
            borderLeft: `3px solid ${issue.level === "error" ? "#ef5350" : "#ffa726"}`,
          }}
        >
          <span
            style={{
              fontSize: 10,
              fontWeight: "bold",
              color: issue.level === "error" ? "#ef5350" : "#ffa726",
              marginRight: 6,
            }}
          >
            {issue.level.toUpperCase()}
          </span>
          <span style={{ color: "#aaa", marginRight: 6 }}>[{issue.code}]</span>
          <span>{issue.message}</span>
          {(issue.nodeId || issue.edgeId) && (
            <div style={{ fontSize: 11, color: "#666", marginTop: 2 }}>
              {issue.nodeId && `node: ${issue.nodeId}`}
              {issue.edgeId && `edge: ${issue.edgeId}`}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  height: 160,
  background: "#0d1117",
  borderTop: "1px solid #333",
  padding: "8px 16px",
  overflowY: "auto",
  fontSize: 12,
  color: "#e0e0e0",
};

const issueStyle: React.CSSProperties = {
  padding: "4px 8px",
  marginBottom: 4,
  background: "#111827",
  borderRadius: 4,
};
