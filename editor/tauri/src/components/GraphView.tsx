import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type Connection,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useEffect } from "react";
import { useDSL } from "../store/dslStore";
import StartNode from "./nodes/StartNode";
import BlockNode from "./nodes/BlockNode";
import EndNode from "./nodes/EndNode";

const nodeTypes: NodeTypes = {
  start: StartNode,
  block: BlockNode,
  end: EndNode,
};

function dslToRFNodes(doc: import("../types/dsl").DSLDocument): Node[] {
  return doc.flows.flatMap((flow) =>
    flow.nodes.map((n) => ({
      id: n.id,
      type: n.type,
      position: { x: n.ui?.x ?? 0, y: n.ui?.y ?? 0 },
      data: { label: n.id, description: n.description ?? "" },
    }))
  );
}

function dslToRFEdges(doc: import("../types/dsl").DSLDocument): Edge[] {
  return doc.flows.flatMap((flow) =>
    flow.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.result ?? "",
      animated: false,
    }))
  );
}

export default function GraphView() {
  const { state, dispatch } = useDSL();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // DSL が変わったら ReactFlow の nodes/edges を更新する
  useEffect(() => {
    if (!state.doc) return;
    setNodes(dslToRFNodes(state.doc));
    setEdges(dslToRFEdges(state.doc));
  }, [state.doc, setNodes, setEdges]);

  // ノード移動後に DSL 側の ui.x / ui.y を更新する
  const handleNodesChange = useCallback(
    (changes: Parameters<typeof onNodesChange>[0]) => {
      onNodesChange(changes);
      for (const change of changes) {
        if (change.type === "position" && change.position) {
          dispatch({
            type: "UPDATE_NODE_POS",
            nodeId: change.id,
            x: change.position.x,
            y: change.position.y,
          });
        }
      }
    },
    [onNodesChange, dispatch]
  );

  // 新しい Edge が接続されたら DSL 側に追加する
  const handleConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
      const newEdge: import("../types/dsl").DSLEdge = {
        id: `edge_${Date.now()}`,
        source: connection.source,
        target: connection.target,
      };
      dispatch({ type: "ADD_EDGE", edge: newEdge });
    },
    [setEdges, dispatch]
  );

  // ノード選択
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      dispatch({ type: "SELECT_NODE", nodeId: node.id });
    },
    [dispatch]
  );

  // エッジ選択
  const handleEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      dispatch({ type: "SELECT_EDGE", edgeId: edge.id });
    },
    [dispatch]
  );

  if (!state.doc) {
    return (
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#666",
        }}
      >
        File → Open でJSONファイルを開いてください
      </div>
    );
  }

  return (
    <div style={{ flex: 1 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={handleConnect}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
