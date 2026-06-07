import { Handle, Position, type NodeProps } from "@xyflow/react";

export default function StartNode({ data }: NodeProps) {
  return (
    <div
      style={{
        background: "#1a4a1a",
        border: "2px solid #4caf50",
        borderRadius: 24,
        padding: "8px 20px",
        color: "#4caf50",
        fontWeight: "bold",
        fontSize: 13,
        minWidth: 80,
        textAlign: "center",
      }}
    >
      <div>START</div>
      <div style={{ fontSize: 11, color: "#aaa" }}>{String(data.label ?? "")}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
