# 02. TestFlow DSL Language Specification

## 1. 基本方針

TestFlow DSL は、テストロジックをノードとエッジで表現する JSON DSL である。

```text
Flow
├─ nodes[]
└─ edges[]
```

DSL の構造は `nodes[] / edges[]` 型に固定する。

## 2. JSONは直接実行しない

JSON DSL は保存形式であり、直接実行形式ではない。

処理の流れは以下である。

```text
JSON DSL
  ↓ Parser
AST / Parsed Model
  ↓ Semantic Validator
IR
  ↓ Backend Compiler
Compiled Plan
  ↓ Runtime
Result Log
```

## 3. 最小DSLの構成

```json
{
  "dslVersion": "0.1.0",
  "flows": []
}
```

`flows[]` は複数のテストフローを持つ。`metadata` はオプションである。

## 4. Metadata

トップレベルのオプション項目である。実行意味論に影響しない。

```json
{
  "metadata": {
    "name": "テスト名",
    "description": "説明",
    "createdBy": "author",
    "createdAt": "2026-01-01",
    "updatedAt": "2026-01-01"
  }
}
```

## 5. Flow

Flow は1つのテストロジック単位である。

必須項目：

```text
id
name
nodes
edges
```

オプション項目：

```text
description
evaluation
```

## 6. Evaluation

`flow.evaluation` はフロー評価方針を定義する。

```json
{
  "evaluation": {
    "enabled": true,
    "aggregation": "failIfAnyBlockFails"
  }
}
```

`enabled=true` の場合、`aggregation` は必須である。

| aggregation | 意味 |
|---|---|
| `failIfAnyBlockFails` | いずれかのブロックが FAIL なら全体 FAIL |
| `passIfAllBlocksPass` | 全ブロックが PASS なら全体 PASS |
| `customExternalEvaluator` | 外部評価器に委ねる |

`enabled=false` の場合、Flow 遷移条件は評価するが最終集計結果は `NOT_EVALUATED` とする。

## 7. Node

初期対応する node type は以下である。

| type | 役割 |
|---|---|
| `start` | フロー開始点 |
| `end` | フロー終了点 |
| `block` | テストブロック |
| `action` | 入力設定などのアクション |
| `condition` | 条件評価ノード |
| `timer` | 時間条件ノード |

将来対応候補：

```text
sequence
parallel
join
externalProcessor
runtimeFeedback
evaluation
tableLookup
interpolation
```

## 8. Edge

Edge はノード間の接続であり、遷移条件を持てる。

```json
{
  "id": "EDGE-001",
  "source": "BLOCK-001",
  "target": "END",
  "priority": 1,
  "condition": {},
  "actions": [],
  "result": "PASS"
}
```

条件なし Edge は無条件遷移を意味する。

`priority` は同一 `source` からの複数 Edge が同時成立した場合の優先順位である（小さいほど高優先）。

## 9. Action

Edge の `actions[]` に指定する遷移時アクションである。

```json
{
  "action": "setInput",
  "signal": "throttle",
  "value": 1.0,
  "applyTiming": "immediate"
}
```

| action | 意味 |
|---|---|
| `setInput` | 入力値を設定する |
| `setSignal` | 信号値を設定する |
| `callExternalProcessor` | 外部プロセッサを呼び出す |

`applyTiming` はアクション適用タイミングである。

| applyTiming | 意味 |
|---|---|
| `immediate` | 即時適用 |
| `nextSample` | 次サンプル適用 |
| `blockStart` | ブロック開始時適用 |

## 10. Condition

初期対応する condition は以下である。

```text
comparison
timeout
anyOf
allOf
not
```

### 10.1 comparison

```json
{
  "type": "comparison",
  "left": { "source": "observed", "signal": "vehicleSpeed" },
  "operator": "greaterThanOrEqual",
  "right": { "value": 100.0 },
  "unit": "km/h"
}
```

`operator` の種類：

| operator | 意味 |
|---|---|
| `equals` | == |
| `notEquals` | != |
| `greaterThan` | > |
| `greaterThanOrEqual` | >= |
| `lessThan` | < |
| `lessThanOrEqual` | <= |
| `risingEdge` | 立ち上がりエッジ |
| `fallingEdge` | 立ち下がりエッジ |

### 10.2 timeout

```json
{
  "type": "timeout",
  "clock": "elapsedBlockSimulationTime",
  "value": 60.0,
  "unit": "s"
}
```

`clock` の種類：

| clock | 意味 |
|---|---|
| `elapsedBlockSimulationTime` | ブロック開始からの経過シミュレーション時間 |
| `simulationTime` | シミュレーション開始からの絶対シミュレーション時間 |
| `wallClockTime` | 実時間（壁時計） |
| `sampleIndex` | サンプルインデックス |

`unit` は `s`、`ms`、`sample` を取れる。

### 10.3 Operand

`comparison` の `left` / `right` は Operand である。

**SignalOperand** — 信号参照：

```json
{ "source": "observed", "signal": "vehicleSpeed" }
```

`source` の種類：

| source | 意味 |
|---|---|
| `input` | 入力信号 |
| `observed` | 観測信号 |
| `derived` | 導出信号 |
| `reference` | 参照値 |
| `clock` | クロック信号 |
| `state` | 状態値 |

**ValueOperand** — 定数値：

```json
{ "value": 100.0 }
```

`value` は `string`、`number`、`integer`、`boolean`、`null` を取れる。

## 11. Result

Edge によってブロック結果を設定できる。

```text
PASS
FAIL
SKIP
ERROR
NOT_EVALUATED
```

`evaluation.enabled=false` の場合でも、Flow 遷移条件は評価する。ただし最終集計結果は `NOT_EVALUATED` とする。

## 12. UI情報

NodeEditor 用の情報は `ui` に分離する。

```json
{
  "id": "BLOCK-001",
  "type": "block",
  "ui": {
    "position": { "x": 100, "y": 200 },
    "label": "Speed Check",
    "collapsed": false
  },
  "data": {
    "description": "60秒以内に100km/hを超えること"
  }
}
```

`ui` は実行意味論に影響しない。

## 13. v0.2以降の階層並列

階層並列は v0.2 系で扱う。

```text
sequence
parallel
block
```

`parallel` には以下が必要である。

```text
joinPolicy
failurePolicy
resultAggregation
resourceConflictPolicy
```

これは v0.1 の Flat Flow が成立した後に導入する。
