# testflow-dsl

`testflow-dsl` は、テストロジックをツール非依存に記述し、NodeEditor で編集し、複数バックエンドで実行するための DSL 設計プロジェクトである。

```text
NodeEditor
  ↓
JSON DSL
  ↓
Parser / Semantic Validator
  ↓
IR / Intermediate Representation
  ↓
Backend Adapter
  ├─ Python Runtime
  ├─ OpenTAP Backend
  ├─ MATLAB / Simulink Backend
  ├─ UE Backend
  └─ HILS / External Tool Backend
```

## 採用した方針

| 項目                     | 採用案                                                       |
| ------------------------ | ------------------------------------------------------------ |
| プロジェクト名           | `testflow-dsl`                                               |
| DSL保存形式              | `nodes` / `edges` 型 JSON                                    |
| 実行方式                 | JSON を直接実行せず、IR に変換してから実行する               |
| 最初のバックエンド       | Python Runtime                                               |
| NodeEditor               | DSL Core / IR / Runtime PoC の後に MVP を作る                |

## ディレクトリ構成

```text
testflow-dsl/
├─ schemas/
│  └─ testflow-dsl.schema.json
├─ examples/
│  └─ simple_speed_flow.json
├─ docs/
│  ├─ 01_project_concept.md
│  ├─ 02_testflow_dsl_language_spec.md
│  ├─ 03_architecture_nodeeditor_jsondsl_backend.md
│  ├─ 04_roadmap.md
│  ├─ 05_backend_strategy.md
│  ├─ 07_ir_specification.md
│  ├─ 08_validation_strategy.md
│  ├─ 09_core_design.md
│  └─ adr/
│     └─ ADR-002-adopt-testflow-dsl-nodeeditor-multibackend.md
├─ src/
│  ├─ core/
│  └─ backends/
└─ scripts/
   └─ validate_testflow.py
```

## 最小DSLの例

```json
{
  "dslVersion": "0.1.0",
  "flows": [
    {
      "id": "FLOW-001",
      "name": "Vehicle speed test",
      "nodes": [
        { "id": "START", "type": "start" },
        {
          "id": "BLOCK-001",
          "type": "block",
          "data": {
            "description": "60秒以内に100km/hを超えること"
          }
        },
        { "id": "END", "type": "end" }
      ],
      "edges": [
        { "id": "EDGE-001", "source": "START", "target": "BLOCK-001" },
        {
          "id": "EDGE-002",
          "source": "BLOCK-001",
          "target": "END",
          "condition": {
            "type": "comparison",
            "left": { "source": "observed", "signal": "vehicleSpeed" },
            "operator": "greaterThanOrEqual",
            "right": { "value": 100.0 },
            "unit": "km/h"
          },
          "result": "PASS"
        },
        {
          "id": "EDGE-003",
          "source": "BLOCK-001",
          "target": "END",
          "condition": {
            "type": "timeout",
            "clock": "elapsedBlockSimulationTime",
            "value": 60.0,
            "unit": "s"
          },
          "result": "FAIL"
        }
      ]
    }
  ]
}
```

## 重要な設計原則

- JSON は保存形式であり、直接実行形式ではない。
- NodeEditor の UI 情報と実行意味論は分離する。
- DSL は Parser / Semantic Validator を通して IR に変換する。
- Backend は IR を受け取り、自分の capability に応じて compile / run する。
- MATLAB/Simulink 依存を避けるため、DSLは特定ツール非依存にする。
