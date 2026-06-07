import { open, save } from "@tauri-apps/plugin-dialog";
import { readTextFile, writeTextFile } from "@tauri-apps/plugin-fs";
import { Command } from "@tauri-apps/plugin-shell";
import { useDSL } from "../store/dslStore";
import type { DSLDocument, ValidationIssue } from "../types/dsl";

export default function MenuBar() {
  const { state, dispatch } = useDSL();

  async function handleOpen() {
    const path = await open({
      filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (!path || typeof path !== "string") return;

    const text = await readTextFile(path);
    const doc = JSON.parse(text) as DSLDocument;
    dispatch({ type: "LOAD", doc, filePath: path });
  }

  async function handleSave() {
    if (!state.doc) return;
    const path = state.filePath ?? (await handleSaveAs());
    if (!path) return;
    await writeTextFile(path, JSON.stringify(state.doc, null, 2));
    dispatch({ type: "MARK_SAVED", filePath: path });
  }

  async function handleSaveAs(): Promise<string | null> {
    if (!state.doc) return null;
    const path = await save({
      defaultPath: state.filePath ?? "flow.json",
      filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (!path) return null;
    await writeTextFile(path, JSON.stringify(state.doc, null, 2));
    dispatch({ type: "MARK_SAVED", filePath: path });
    return path;
  }

  async function handleValidate() {
    if (!state.filePath) {
      await handleSave();
      if (!state.filePath) return;
    }
    try {
      // Python validator を外部実行する
      const output = await Command.create("python3", [
        "-m", "testflow_validator",
        "--json-output",
        state.filePath,
      ]).execute();

      const issues: ValidationIssue[] = JSON.parse(output.stdout || "[]");
      dispatch({ type: "SET_ISSUES", issues });
    } catch {
      dispatch({
        type: "SET_ISSUES",
        issues: [
          {
            level: "error",
            code: "VALIDATOR_ERROR",
            message: "Validator の実行に失敗しました。",
          },
        ],
      });
    }
  }

  const title =
    (state.filePath ? state.filePath.split("/").pop() : "未保存") +
    (state.dirty ? " *" : "");

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        height: 36,
        background: "#161b22",
        borderBottom: "1px solid #333",
        padding: "0 12px",
        gap: 8,
        userSelect: "none",
      }}
    >
      <MenuButton label="Open" onClick={handleOpen} shortcut="Ctrl+O" />
      <MenuButton
        label="Save"
        onClick={handleSave}
        shortcut="Ctrl+S"
        disabled={!state.doc}
      />
      <MenuButton
        label="Save As…"
        onClick={handleSaveAs}
        disabled={!state.doc}
      />
      <div style={{ width: 1, height: 20, background: "#444", margin: "0 4px" }} />
      <MenuButton
        label="Validate"
        onClick={handleValidate}
        shortcut="Ctrl+Shift+V"
        disabled={!state.doc}
      />
      <div style={{ flex: 1, textAlign: "center", fontSize: 12, color: "#888" }}>
        {title}
      </div>
    </div>
  );
}

function MenuButton({
  label,
  onClick,
  shortcut,
  disabled,
}: {
  label: string;
  onClick: () => void;
  shortcut?: string;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={shortcut}
      style={{
        background: "none",
        border: "none",
        color: disabled ? "#555" : "#ccc",
        cursor: disabled ? "default" : "pointer",
        fontSize: 13,
        padding: "4px 10px",
        borderRadius: 4,
      }}
    >
      {label}
    </button>
  );
}
