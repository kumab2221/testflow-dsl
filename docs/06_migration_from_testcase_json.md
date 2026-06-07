# 06. Migration from testcase JSON

## 1. 旧方針

旧方針では、テストケース定義を以下のように扱っていた。

```text
root
├─ schemaVersion
├─ testSuite
├─ defaults
├─ testCases[]
└─ metadata
```

各 testCase は以下を持っていた。

```text
execution
inputSources
signalProcessing
runtimeFeedback
flow.blocks[]
evaluation
revision
```

## 2. 新方針

新方針では、NodeEditorとの親和性を優先し、以下へ移行する。

```text
root
├─ dslVersion
└─ flows[]
   ├─ nodes[]
   └─ edges[]
```

## 3. 旧 flow.blocks[] から nodes/edges への対応

| 旧構造 | 新構造 |
|---|---|
| `flow.startBlock` | `start` node からの edge |
| `flow.blocks[]` | `nodes[type=block]` |
| `block.transitions[]` | `edges[]` |
| `transition.when` | `edge.condition` |
| `transition.result` | `edge.result` |
| `transition.nextBlock` | `edge.target` |

## 4. 旧Schemaの扱い

旧 `testcase-suite.schema.json` は破棄しない。

扱いは以下とする。

```text
- DSL設計の参考資料
- v0.1要件のトレーサビリティ資料
- migration仕様の入力資料
```

ただし、新規開発の中心は `testflow-dsl.schema.json` とする。

## 5. 継承する考え方

旧方針から継承するもの：

```text
- JSONでGit管理する
- 大きな時系列データは外部参照にする
- evaluation.enabled と flow遷移は分ける
- 判定OFF時は NOT_EVALUATED とする
- runtimeFeedbackは限定的に導入する
- 自然言語条件は実行対象にしない
- condition/actionは構造化する
```

## 6. 捨てる/再設計するもの

再設計するもの：

```text
- flow.blocks[] 形式
- testCase 中心の構造
- 人間が直接編集しやすいJSON構造
```

理由：

```text
NodeEditor + DSL + Backend を前提にすると、nodes/edges 型の方が自然であるため。
```

## 7. 移行方針

移行ツールを将来作る場合の流れ：

```text
旧 testcase-suite JSON
  ↓
Legacy Parser
  ↓
TestFlow IR
  ↓
New JSON DSL Exporter
```

直接 `旧JSON → 新JSON` にしない。IRを経由する。
