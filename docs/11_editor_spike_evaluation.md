# 11. NodeEditor Spike 評価記録

## 1. 概要

Phase 4 では C++ + Dear ImGui 案と Rust + Tauri 案を spike ブランチで並走し、評価結果を本ドキュメントに記録する。

詳細な要件・判断基準は [docs/10_editor_mvp_requirements.md](10_editor_mvp_requirements.md) を参照。

---

## 2. 案A: C++ + Dear ImGui + imgui-node-editor

### 2.1 構成

```text
Language:     C++20 or C++23
GUI:          Dear ImGui + imgui-node-editor
Window:       GLFW + OpenGL3 または SDL2 + OpenGL3
JSON:         nlohmann/json
Build:        CMake
Validation:   Python validator を外部実行（初期）
Branch:       spike/editor-cpp-imgui-crossplatform
```

### 2.2 強み

```text
- UE Blueprint 風の NodeEditor に寄せやすい
- ネイティブアプリとして軽い
- C++ Runtime / C++ Backend と相性が良い
- Windows / Ubuntu の両方で動かしやすい
- リアルタイム描画やツール UI に向いている
- 将来的に UE 連携や C++ 系ツール連携を意識しやすい
```

### 2.3 弱み

```text
- Property Panel の作り込みが自前になりやすい
- undo / redo / copy / paste が自前寄り
- ファイルダイアログや OS 連携に追加実装が必要
- JSON Schema validation を C++ で完結するには追加調査が必要
- 日本語入力・フォント・IME 対応は必ず検証が必要
- UI テストがしにくい
- Web 化は弱い
```

### 2.4 Ubuntu での確認項目

| 確認項目 | 結果 | 備考 |
|---|---|---|
| Ubuntu でビルドできるか | - | |
| Ubuntu で起動できるか | - | |
| X11 / Wayland 環境で問題がないか | - | |
| OpenGL / GLFW / SDL の依存が重くないか | - | |
| 日本語フォントが表示できるか | - | |
| 日本語入力ができるか | - | |
| ファイル選択ダイアログが使えるか | - | |
| HiDPI 表示が崩れないか | - | |

### 2.5 MVP 達成状況

| ID | 内容 | 結果 | 備考 |
|---|---|---|---|
| MVP-01 | simple_speed_flow.json を読み込む | - | |
| MVP-02 | StartNode / BlockNode / EndNode を表示する | - | |
| MVP-03 | ノードを移動できる | - | |
| MVP-04 | Edge を接続できる | - | |
| MVP-05 | BlockNode の description を編集できる | - | |
| MVP-06 | Edge の condition を編集できる | - | |
| MVP-07 | Action を選択できる | - | |
| MVP-08 | JSON として保存できる | - | |
| MVP-09 | Validator を呼び出しエラーを表示できる | - | |
| MVP-10 | 日本語 description を入力・保存・再読込できる | - | |
| MVP-11 | Ubuntu と Windows の両方で起動できる | - | |

### 2.6 実装コスト

```text
着手日:    -
MVP達成日: -
工数:      -
詰まった点: -
```

---

## 3. 案B: Rust + Tauri + React Flow

### 3.1 構成

```text
Frontend:   TypeScript + React + React Flow
Shell:      Tauri
Core:       Rust
Validation: Rust Core または TypeScript / Ajv
Build:      pnpm / npm + cargo
Branch:     spike/editor-rust-tauri-crossplatform
```

### 3.2 強み

```text
- React Flow により NodeEditor MVP を作りやすい
- Property Panel やフォーム編集を作りやすい
- JSON DSL / JSON Schema / TypeScript 型との相性が良い
- Tauri により Windows / Ubuntu 両対応しやすい
- Rust Core に DSL Parser / Validator / IR を置ける
- 将来的に Web 版へ展開しやすい
- UI と Core を分離しやすい
```

### 3.3 弱み

```text
- UE 風のネイティブ感は C++ + ImGui より弱い
- Tauri / Rust / TypeScript の複合構成になる
- Linux では WebKitGTK などの依存が必要
- フロントエンドのビルド環境管理が必要
- C++ Backend との直接親和性は C++ 案より弱い
```

### 3.4 Ubuntu での確認項目

| 確認項目 | 結果 | 備考 |
|---|---|---|
| Ubuntu で Tauri の依存関係を導入できるか | - | |
| Ubuntu でビルドできるか | - | |
| Ubuntu で起動できるか | - | |
| 日本語入力ができるか | - | |
| 日本語保存・再読込ができるか | - | |
| ファイルダイアログが使えるか | - | |
| AppImage / deb 配布が現実的か | - | |
| Windows とのビルド差分が許容できるか | - | |

### 3.5 MVP 達成状況

| ID | 内容 | 結果 | 備考 |
|---|---|---|---|
| MVP-01 | simple_speed_flow.json を読み込む | - | |
| MVP-02 | StartNode / BlockNode / EndNode を表示する | - | |
| MVP-03 | ノードを移動できる | - | |
| MVP-04 | Edge を接続できる | - | |
| MVP-05 | BlockNode の description を編集できる | - | |
| MVP-06 | Edge の condition を編集できる | - | |
| MVP-07 | Action を選択できる | - | |
| MVP-08 | JSON として保存できる | - | |
| MVP-09 | Validator を呼び出しエラーを表示できる | - | |
| MVP-10 | 日本語 description を入力・保存・再読込できる | - | |
| MVP-11 | Ubuntu と Windows の両方で起動できる | - | |

### 3.6 実装コスト

```text
着手日:    -
MVP達成日: -
工数:      -
詰まった点: -
```

---

## 4. 比較サマリ

| 評価項目 | 案A: C++ + ImGui | 案B: Rust + Tauri |
|---|---|---|
| Ubuntu ビルド | - | - |
| Windows ビルド | - | - |
| JSON 互換性 | - | - |
| 日本語入力 | - | - |
| Node 操作感 | - | - |
| Property Panel | - | - |
| Validation 表示 | - | - |
| 保守性 | - | - |
| 配布性 | - | - |

---

## 5. 採用判断

```text
判断日:     -
採用技術:   -
不採用技術: -
理由:       -
ADR:        docs/adr/ADR-003-editor-technology-selection.md
```
