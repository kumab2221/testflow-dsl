# 02. TestFlow DSL Language Specification

## 1. 基本方針

TestFlow DSL は、テストロジックをノードとエッジで表現する JSON DSL である。

```text
Flow
├─ nodes[]
└─ edges[]
```

NodeEditor との親和性を優先し、旧 `flow.blocks[]` 形式ではなく、`nodes[] / edges[]` 型を採用する。

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

`flows[]` は複数のテストフローを持つ。

## 4. Flow

Flow は1つのテストロジック単位である。

必須項目：

```text
id
name
nodes
edges
```

## 5. Node

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

## 6. Edge

Edge はノード間の接続であり、遷移条件を持てる。

```json
{
  "id": "EDGE-001",
  "source": "BLOCK-001",
  "target": "END",
  "condition": {},
  "result": "PASS"
}
```

条件なし Edge は無条件遷移を意味する。

## 7. Condition

初期対応する condition は以下である。

```text
comparison
timeout
anyOf
allOf
not
```

### 7.1 comparison

```json
{
  "type": "comparison",
  "left": { "source": "observed", "signal": "vehicleSpeed" },
  "operator": "greaterThanOrEqual",
  "right": { "value": 100.0 },
  "unit": "km/h"
}
```

### 7.2 timeout

```json
{
  "type": "timeout",
  "clock": "elapsedBlockSimulationTime",
  "value": 60.0,
  "unit": "s"
}
```

`elapsedBlockSimulationTime` はブロック開始からの経過シミュレーション時間を意味する。

## 8. Result

Edge によってブロック結果を設定できる。

```text
PASS
FAIL
SKIP
ERROR
NOT_EVALUATED
```

`evaluation.enabled=false` の場合でも、Flow 遷移条件は評価する。ただし最終集計結果は `NOT_EVALUATED` とする。

## 9. UI情報

NodeEditor 用の情報は `ui` に分離する。

```json
{
  "id": "BLOCK-001",
  "type": "block",
  "ui": {
    "position": { "x": 100, "y": 200 },
    "collapsed": false
  },
  "data": {
    "description": "60秒以内に100km/hを超えること"
  }
}
```

`ui` は実行意味論に影響しない。

## 10. v0.2以降の階層並列

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
