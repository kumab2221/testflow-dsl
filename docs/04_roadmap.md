# 04. Roadmap

## 1. 基本方針

旧ロードマップは `testcase JSON tools` を前提にしていた。今後は `Test Logic DSL + NodeEditor + Multiple Backends` を前提にする。

ただし、いきなりNodeEditorから作ってはいけない。順番は以下である。

```text
DSL仕様
↓
IR
↓
Validator
↓
Runtime PoC
↓
NodeEditor
↓
Parallel / Multiple Backends
```

## Phase 0: 方針再定義

目的：

```text
プロジェクトを testcase JSON tools から testflow-dsl へ切り替える。
```

成果物：

```text
README.md
docs/01_project_concept.md
docs/03_architecture_nodeeditor_jsondsl_backend.md
docs/adr/ADR-002-adopt-testflow-dsl-nodeeditor-multibackend.md
```

完了条件：

```text
- プロジェクト名が testflow-dsl として定義されている
- JSON DSL + NodeEditor + Multiple Backends 方針が文書化されている
- OpenTAPとの住み分けが明確である
```

## Phase 1: DSL Core

目的：

```text
最小のテストロジックを表現できるDSLを作る。
```

対象：

```text
- flow
- nodes
- edges
- block
- condition
- timeout
- action
- result
```

成果物：

```text
schemas/testflow-dsl.schema.json
docs/02_testflow_dsl_language_spec.md
examples/simple_speed_flow.json
```

完了条件：

```text
- simple_speed_flow.json が Schema 検証に通る
- 60秒以内に100km/h到達、未達ならFAILというロジックを表現できる
```

## Phase 2: Parser / Validator / IR

目的：

```text
JSON DSLを読み、検証し、IRへ変換する。
```

成果物：

```text
src/core/parser
src/core/semantic_validator
src/core/ir
src/core/type_checker
```

検証内容：

```text
- node.id 重複
- edge.id 重複
- edge.source / edge.target の存在
- start node の存在
- end node の存在
- 到達不能node
- 無限ループ可能性
- condition内のsignal参照
- result指定の妥当性
```

完了条件：

```text
- JSON DSLをIRへ変換できる
- 参照整合性エラーを検出できる
```

## Phase 3: Python Runtime Backend

目的：

```text
最小DSLを実行できるバックエンドを作る。
```

対応範囲：

```text
- sequence相当の単純フロー
- block
- edge condition
- timeout
- result log
```

完了条件：

```text
- simple_speed_flow.json を実行できる
- PASS/FAIL/NOT_EVALUATED をログ出力できる
- evaluation.enabled=falseでもFlow遷移は評価できる
```

## Phase 4: NodeEditor MVP

目的：

```text
JSONを手書きせずにDSLを作れるようにする。
```

対応範囲：

```text
- Start / Block / End node
- Edge作成
- Condition編集
- Timeout編集
- JSON保存/読込
- Schema / Semantic validation 表示
```

完了条件：

```text
- NodeEditorで simple_speed_flow.json 相当のDSLを作れる
- 保存したJSONをPython Runtimeで実行できる
```

## Phase 5: Hierarchical Flow / Parallel

目的：

```text
sequence / parallel / nested parallel をDSLに入れる。
```

追加概念：

```text
- sequence node
- parallel node
- joinPolicy
- failurePolicy
- resultAggregation
- resourceConflictPolicy
```

完了条件：

```text
- 並列内並列をDSLで表現できる
- Backend capabilityで未対応機能を検出できる
- resource conflict を検出できる
```

## Phase 6: Backend Adapter拡張

目的：

```text
複数バックエンド運用へ進める。
```

候補：

```text
- OpenTAP Backend
- MATLAB / Simulink Backend
- C++ Backend
- UE Backend
- HILS Backend
```

優先順位：

```text
1. Python Runtime
2. OpenTAP Backend評価
3. C++ or external tool backend
4. MATLAB / Simulink backend
5. UE / HILS backend
```

## 2. 重要な判断基準

v0.2相当の並列化に進む前に、以下を満たすこと。

```text
- DSL Core が安定している
- IR が定義されている
- Semantic Validator がある
- Python Runtime PoC が動く
- Result Log が出力できる
- NodeEditor MVP が最低限動く
```

これを満たさずに並列化へ進むと、設計が破綻する可能性が高い。
