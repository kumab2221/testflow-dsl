# 07. IR Specification

## 1. IRの目的

IR は JSON DSL と Backend の間に置く中間表現である。

```text
JSON DSL → IR → Backend
```

JSON DSLは保存形式、IRは実行・変換用表現である。

## 2. IRを分ける理由

```text
- NodeEditorのUI情報を排除する
- Backendごとの差分を吸収する
- Semantic Validation後の安全な表現にする
- Version Migrationを容易にする
- 最適化や変換を行いやすくする
```

## 3. IRの最小構造

```json
{
  "irVersion": "0.1.0",
  "flows": [
    {
      "id": "FLOW-001",
      "name": "Vehicle speed test",
      "startNodeId": "START",
      "nodes": [],
      "edges": []
    }
  ]
}
```

## 4. IR Node

IR Node には UI 情報を含めない。

```json
{
  "id": "BLOCK-001",
  "type": "block",
  "description": "60秒以内に100km/hを超えること",
  "entryActions": []
}
```

## 5. IR Edge

```json
{
  "id": "EDGE-002",
  "source": "BLOCK-001",
  "target": "END",
  "condition": {
    "type": "comparison",
    "left": {
      "source": "observed",
      "signal": "vehicleSpeed"
    },
    "operator": "greaterThanOrEqual",
    "right": {
      "value": 100.0
    }
  },
  "result": "PASS"
}
```

## 6. IRで正規化するもの

```text
- condition の表現
- operator の内部表現
- clock の参照
- node/edge の参照
- default値
- capability検証用feature一覧
```

## 7. v0.2で追加するIR

```text
SequenceNode
ParallelNode
JoinPolicy
FailurePolicy
ResultAggregation
ResourceConflictPolicy
```

v0.2ではIRが重要になる。JSON DSLの見た目に引っ張られてBackendを作らないこと。
