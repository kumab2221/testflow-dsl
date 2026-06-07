import { Handle, Position, type NodeProps } from "@xyflow/react";

export default function EndNode({ data }: NodeProps) {
  return (
    <div
      style={{
        background: "#4a1a1a",
        border: "2px solid #ef5350",
        borderRadius: 24,
        padding: "8px 20px",
        color: "#ef5350",
        fontWeight: "bold",
        fontSize: 13,
        minWidth: 80,
        textAlign: "center",
      }}
    >
      <Handle type="target" position={Position.Top} />
      <div>END</div>
      <div style={{ fontSize: 11, color: "#aaa" }}>{String(data.label ?? "")}</div>
    </div>
  );
}
