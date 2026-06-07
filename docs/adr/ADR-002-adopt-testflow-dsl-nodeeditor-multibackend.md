# ADR-002: Adopt TestFlow DSL + NodeEditor + Multiple Backends

## Status

Accepted

## Context

当初は、テストケースをJSONで運用・管理し、使用時ツールと編集時ツールを作る方針だった。

しかし検討を進める中で、以下の要件が明確になった。

```text
- テストブロックの遷移
- success / timeout / condition
- simulationTime
- runtimeFeedback
- 将来的な階層並列
- NodeEditorによるロジック作成
- OpenTAP / Python / MATLAB / UE / HILS など複数バックエンド
```

これは単なるJSON管理ツールではなく、テストロジックDSLに近い。

## Decision

プロジェクト方針を以下へ変更する。

```text
Test Logic DSL + NodeEditor + Multiple Backends
```

プロジェクト名は `testflow-dsl` とする。

採用する設計：

```text
- JSON DSL は nodes/edges 型とする
- JSONは保存形式であり、直接実行しない
- IRを別に定義する
- 最初のBackendは Python Runtime とする
- OpenTAPは後続フェーズでBackend候補として評価する
- NodeEditorはDSL Core / IR / Runtime PoC の後に作る
```

## Consequences

メリット：

```text
- MATLAB/Simulink依存を避けられる
- OpenTAPとも住み分けできる
- NodeEditorとの親和性が高い
- 複数Backendに展開しやすい
- テストロジックをGit管理しやすい
```

デメリット：

```text
- スコープが大きくなる
- DSL仕様、Parser、IR、Validator、Runtimeが必要になる
- NodeEditorを先に作ると破綻しやすい
- Backend差分を吸収する設計が必要になる
```

## Rejected Options

### 1. testcase JSON tools のまま進める

却下理由：

```text
NodeEditor、複数Backend、階層並列を考えると testCase 中心のJSON構造では拡張が苦しい。
```

### 2. OpenTAPに全面依存する

却下理由：

```text
OpenTAPは実行基盤として強いが、TestFlow DSLのツール非依存なロジック表現を担わせると目的がずれる。
```

### 3. NodeEditorから先に作る

却下理由：

```text
見た目は進むが、DSL仕様とIRが固まっていないため、後で作り直しになる可能性が高い。
```
