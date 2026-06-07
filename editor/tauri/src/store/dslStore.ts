// DSLDocument のグローバル状態を React state で管理する
// 小規模 MVP なので Zustand 等は使わず useReducer + Context で実装する

import { createContext, useContext } from "react";
import type { DSLDocument, ValidationIssue } from "../types/dsl";

export interface DSLState {
  doc: DSLDocument | null;
  filePath: string | null;
  dirty: boolean;
  issues: ValidationIssue[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
}

export type DSLAction =
  | { type: "LOAD"; doc: DSLDocument; filePath: string }
  | { type: "SET_DIRTY" }
  | { type: "MARK_SAVED"; filePath: string }
  | { type: "SET_ISSUES"; issues: ValidationIssue[] }
  | { type: "SELECT_NODE"; nodeId: string | null }
  | { type: "SELECT_EDGE"; edgeId: string | null }
  | { type: "UPDATE_NODE_DESC"; nodeId: string; description: string }
  | { type: "UPDATE_NODE_POS"; nodeId: string; x: number; y: number }
  | { type: "UPDATE_EDGE_RESULT"; edgeId: string; result: string | undefined }
  | { type: "UPDATE_EDGE_PRIORITY"; edgeId: string; priority: number }
  | { type: "ADD_EDGE"; edge: import("../types/dsl").DSLEdge }
  | { type: "ADD_NODE_ACTION"; nodeId: string; action: import("../types/dsl").Action };

export const initialState: DSLState = {
  doc: null,
  filePath: null,
  dirty: false,
  issues: [],
  selectedNodeId: null,
  selectedEdgeId: null,
};

export function dslReducer(state: DSLState, action: DSLAction): DSLState {
  switch (action.type) {
    case "LOAD":
      return { ...initialState, doc: action.doc, filePath: action.filePath };

    case "SET_DIRTY":
      return { ...state, dirty: true };

    case "MARK_SAVED":
      return { ...state, dirty: false, filePath: action.filePath };

    case "SET_ISSUES":
      return { ...state, issues: action.issues };

    case "SELECT_NODE":
      return { ...state, selectedNodeId: action.nodeId, selectedEdgeId: null };

    case "SELECT_EDGE":
      return { ...state, selectedEdgeId: action.edgeId, selectedNodeId: null };

    case "UPDATE_NODE_DESC": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f) => ({
        ...f,
        nodes: f.nodes.map((n) =>
          n.id === action.nodeId ? { ...n, description: action.description } : n
        ),
      }));
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    case "UPDATE_NODE_POS": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f) => ({
        ...f,
        nodes: f.nodes.map((n) =>
          n.id === action.nodeId
            ? { ...n, ui: { ...n.ui, x: action.x, y: action.y } }
            : n
        ),
      }));
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    case "UPDATE_EDGE_RESULT": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f) => ({
        ...f,
        edges: f.edges.map((e) =>
          e.id === action.edgeId
            ? { ...e, result: action.result as import("../types/dsl").ResultValue | undefined }
            : e
        ),
      }));
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    case "UPDATE_EDGE_PRIORITY": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f) => ({
        ...f,
        edges: f.edges.map((e) =>
          e.id === action.edgeId ? { ...e, priority: action.priority } : e
        ),
      }));
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    case "ADD_EDGE": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f, i) =>
        i === 0 ? { ...f, edges: [...f.edges, action.edge] } : f
      );
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    case "ADD_NODE_ACTION": {
      if (!state.doc) return state;
      const flows = state.doc.flows.map((f) => ({
        ...f,
        nodes: f.nodes.map((n) =>
          n.id === action.nodeId
            ? { ...n, entryActions: [...(n.entryActions ?? []), action.action] }
            : n
        ),
      }));
      return { ...state, dirty: true, doc: { ...state.doc, flows } };
    }

    default:
      return state;
  }
}

export interface DSLContextValue {
  state: DSLState;
  dispatch: React.Dispatch<DSLAction>;
}

export const DSLContext = createContext<DSLContextValue | null>(null);

export function useDSL(): DSLContextValue {
  const ctx = useContext(DSLContext);
  if (!ctx) throw new Error("useDSL must be used within DSLProvider");
  return ctx;
}
