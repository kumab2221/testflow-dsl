import { Handle, Position, type NodeProps } from "@xyflow/react";

export default function BlockNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        background: selected ? "#2a3a5a" : "#1e2a3a",
        border: `2px solid ${selected ? "#64b5f6" : "#42a5f5"}`,
        borderRadius: 8,
        padding: "10px 16px",
        color: "#e0e0e0",
        fontSize: 13,
        minWidth: 140,
      }}
    >
      <Handle type="target" position={Position.Top} />
      <div style={{ fontWeight: "bold", marginBottom: 4 }}>
        BLOCK: {String(data.label ?? "")}
      </div>
      {data.description && (
        <div style={{ fontSize: 11, color: "#aaa", maxWidth: 200, wordBreak: "break-all" }}>
          {String(data.description)}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
