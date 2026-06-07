import { useReducer } from "react";
import { DSLContext, dslReducer, initialState } from "./store/dslStore";
import MenuBar from "./components/MenuBar";
import GraphView from "./components/GraphView";
import PropertyPanel from "./components/PropertyPanel";
import ValidationPanel from "./components/ValidationPanel";

export default function App() {
  const [state, dispatch] = useReducer(dslReducer, initialState);

  return (
    <DSLContext.Provider value={{ state, dispatch }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          background: "#0d1117",
          color: "#e0e0e0",
          fontFamily: "'Noto Sans CJK JP', 'Segoe UI', sans-serif",
        }}
      >
        <MenuBar />
        <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
          <GraphView />
          <PropertyPanel />
        </div>
        <ValidationPanel />
      </div>
    </DSLContext.Provider>
  );
}
