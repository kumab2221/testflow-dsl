# 10. NodeEditor MVP 要件

## 1. 目的

Phase 4 の目的は、TestFlow DSL を手書き JSON ではなく、NodeEditor で安全に作成・編集できるようにすることである。

ただし、Phase 4 で目指すのは完成版の統合開発環境ではない。
最初に作るべきものは、**DSL / IR / Validator / Runtime PoC が成立した後に、その DSL を編集できる最小 NodeEditor MVP** である。

```text
TestFlow DSL
  ↓
NodeEditor で編集
  ↓
JSON DSL として保存
  ↓
Parser / Semantic Validator
  ↓
IR
  ↓
Backend
```

Phase 4 では、特に以下を確認する。

```text
- NodeEditorでDSLを直感的に作れるか
- JSON DSLを壊さずに生成できるか
- Validatorと連携できるか
- Ubuntu / Windows の両方で継続運用できるか
- C++ + ImGui 案と Rust + Tauri 案のどちらが適しているか
```

---

## 2. Phase 4 の位置づけ

### 2.1 Phase 4 より前に完了しておくべきこと

NodeEditor を先に作ると、見た目だけ進んで中身が破綻する。
そのため、Phase 4 の前に以下を完了しておく。

```text
Phase 1: DSL Core
  - nodes / edges 型の TestFlow DSL 仕様
  - JSON Schema
  - simple_speed_flow.json

Phase 2: Parser / Validator / IR
  - JSON DSL の読み込み
  - Semantic Validator
  - IR 変換

Phase 3: Runtime PoC
  - 最小DSLの実行
  - block / transition / condition / timeout
  - result log 出力
```

Phase 4 は、これらの成果物を前提にする。

---

## 3. Phase 4 で作るもの

Phase 4 で作るのは、NodeEditor の最小実用版である。

### 3.1 MVP 対象

| ID | 内容 |
|---|---|
| MVP-01 | `simple_speed_flow.json` を読み込む |
| MVP-02 | StartNode / BlockNode / EndNode を表示する |
| MVP-03 | ノードを移動できる |
| MVP-04 | Edge を接続できる |
| MVP-05 | BlockNode の description を編集できる |
| MVP-06 | Edge の condition を編集できる |
| MVP-07 | Action として setBackendInput / setInternalSignal / callExternalProcessor を選択できる |
| MVP-08 | JSON として保存できる |
| MVP-09 | Validator を呼び出し、エラーを表示できる |
| MVP-10 | 日本語 description を入力・保存・再読込できる |
| MVP-11 | Ubuntu と Windows の両方で起動できる |

### 3.2 Phase 4 では作らないもの

以下は Phase 4 MVP の対象外とする。

```text
- 階層的な並列実行
- nested parallel
- OpenTAP Backend
- MATLAB Backend
- UE Backend
- 高度な Runtime 実行
- 高度なデバッグ機能
- 自動レイアウト
- 大規模グラフ最適化
- 完成版の GUI デザイン
```

---

## 4. 採用候補技術

Phase 4 では、以下の2案を比較する。

```text
案A: C++ + Dear ImGui + imgui-node-editor
案B: Rust + Tauri + React Flow
```

Ubuntu でも使用するため、Windows 前提の評価では不十分である。
Ubuntu / Windows 両対応を必須条件として評価する。

詳細は [docs/11_editor_spike_evaluation.md](11_editor_spike_evaluation.md) を参照。

---

## 5. 共通 MVP 仕様

両ブランチで、同じ MVP を実装する。
これを守らないと比較不能になる。

### 5.1 共通入力

```text
examples/simple_speed_flow.json
```

### 5.2 必須機能

```text
1. JSON を読み込める
2. StartNode / BlockNode / EndNode を表示できる
3. ノードを移動できる
4. Edge を接続できる
5. BlockNode の description を編集できる
6. Edge の condition を編集できる
7. Action を選択できる
   - setBackendInput
   - setInternalSignal
   - callExternalProcessor
8. JSON として保存できる
9. 保存した JSON を再読込できる
10. Validator を呼び出せる
11. Validation error を一覧表示できる
12. 日本語 description を保存・再読込できる
```

### 5.3 Action 定義

Phase 4 MVP では、Action を以下に絞る。

| Action | 意味 |
|---|---|
| `setInternalSignal` | DSL 内部の信号・変数・状態値を変更する |
| `setBackendInput` | Backend の入力ポートへ値を渡す |
| `callExternalProcessor` | 外部プロセッサを呼び出す |

`observed` は Action ではない。
`observed` は Backend 出力ポート・状態値を読む Operand source として扱う。

---

## 6. Operand source の整理

| source | 意味 |
|---|---|
| `backendInput` | Backend 入力ポートへ渡す信号。`setBackendInput` により設定される |
| `observed` | Backend 出力ポート・Backend 状態値を読む |
| `internal` | DSL 内部の信号・変数・状態値。`setInternalSignal` により設定される |
| `derived` | 補間・テーブル参照・外部処理などで導出された信号 |
| `reference` | 目標値・期待値・基準値 |
| `clock` | simulationTime、elapsedBlockSimulationTime、sampleIndex など |

---

## 7. ブランチ戦略

技術選定は main に直接作り込まない。
以下の spike ブランチで並走する。

```text
main
├─ spike/editor-cpp-imgui-crossplatform
└─ spike/editor-rust-tauri-crossplatform
```

### 7.1 main に置くもの

```text
schemas/
  testflow-dsl.schema.json

examples/
  simple_speed_flow.json

docs/
  10_editor_mvp_requirements.md
  11_editor_spike_evaluation.md
```

### 7.2 spike ブランチのルール

```text
- spike ブランチは技術検証用であり、長期運用しない
- 共通 DSL 仕様は main 側で管理する
- spike 側で DSL 仕様を勝手に変更しない
- 仕様変更が必要な場合は main へ反映する
- 最終判断後、不採用ブランチは archive する
```

---

## 8. 評価基準

### 8.1 必須評価項目

| 評価項目 | 内容 |
|---|---|
| Ubuntu 対応 | Ubuntu でビルド・起動できるか |
| Windows 対応 | Windows でビルド・起動できるか |
| JSON 互換性 | 同じ JSON を読み書きできるか |
| 日本語対応 | 日本語入力・保存・再読込が問題ないか |
| Node 操作 | ノード追加・移動・接続が自然か |
| Property Panel | 条件・Action 編集がしやすいか |
| Validation 表示 | エラー箇所を見つけやすいか |
| 保守性 | チームで継続開発できるか |
| 配布性 | Ubuntu / Windows へ配布しやすいか |

### 8.2 加点評価項目

| 評価項目 | C++ + ImGui | Rust + Tauri |
|---|---:|---:|
| UE 風の見た目 | 強い | 中 |
| ネイティブ感 | 強い | 中〜強 |
| JSON / フォーム編集 | 中 | 強い |
| Web 展開 | 弱い | 強い |
| C++ Backend 親和性 | 強い | 中 |
| Rust Core 親和性 | 中 | 強い |
| UI 作成速度 | 中 | 強い |

---

## 9. 採用判断の流れ

### 9.1 判断タイミング

以下のどちらかで判断する。

```text
- 両ブランチが共通 MVP を満たした時点
- 片方が明確に詰まり、継続コストが高いと判断できた時点
```

### 9.2 判断結果の記録

採用判断は ADR に残す。

```text
docs/adr/ADR-003-editor-technology-selection.md
```

記載内容：

```text
- 比較対象
- 実装した MVP 範囲
- 実装コスト
- Ubuntu 対応結果
- Windows 対応結果
- 日本語入力結果
- UI 操作感
- 保守性
- 配布性
- 採用技術
- 不採用技術と理由
```
