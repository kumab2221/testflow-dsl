# 09. Core Design — Phase 2

## 1. 処理フロー概要

```text
JSON ファイル / dict
      │
      ▼
┌─────────────┐   ParseError
│  DSLParser  │──────────────▶ 例外送出
└─────────────┘
      │ DSLFlowIR
      ▼
┌──────────────────┐   ValidationIssue[]
│ SemanticValidator│──────────────────▶ error / warning
└──────────────────┘
      │ DSLFlowIR（構造は変わらない）
      ▼
┌─────────────┐   ValidationIssue[]
│ TypeChecker │──────────────────▶ error / warning
└─────────────┘
      │ DSLFlowIR
      ▼
  Backend Adapter（Phase 3 以降）
```

---

## 2. シーケンス図

```mermaid
sequenceDiagram
    participant Client
    participant DSLParser
    participant jsonschema
    participant SemanticValidator
    participant TypeChecker

    Client->>DSLParser: parse(dsl_path)
    DSLParser->>jsonschema: iter_errors(data)
    jsonschema-->>DSLParser: errors
    alt schema error
        DSLParser-->>Client: raise ParseError
    end
    DSLParser-->>Client: DSLFlowIR

    Client->>SemanticValidator: validate(ir)
    SemanticValidator-->>Client: list[ValidationIssue]

    Client->>TypeChecker: check(ir)
    TypeChecker-->>Client: list[ValidationIssue]
```

---

## 3. クラス図 — IR モデル

```mermaid
classDiagram
    class DSLFlowIR {
        +str ir_version
        +list~FlowIR~ flows
    }

    class FlowIR {
        +str id
        +str name
        +str start_node_id
        +str description
        +list~NodeIR~ nodes
        +list~EdgeIR~ edges
        +EvaluationIR evaluation
    }

    class NodeIR {
        +str id
        +str type
        +str description
        +list~ActionIR~ entry_actions
    }

    class EdgeIR {
        +str id
        +str source
        +str target
        +int priority
        +str result
        +Condition condition
        +list~ActionIR~ actions
    }

    class EvaluationIR {
        +bool enabled
        +str aggregation
    }

    class ActionIR {
        +str action
        +str signal
        +value
        +str processor
        +str apply_timing
    }

    class ComparisonCondition {
        +Operand left
        +str operator
        +Operand right
        +str unit
    }

    class TimeoutCondition {
        +str clock
        +float value
        +str unit
    }

    class AnyOfCondition {
        +list~Condition~ conditions
    }

    class AllOfCondition {
        +list~Condition~ conditions
    }

    class NotCondition {
        +Condition condition
    }

    class SignalOperand {
        +str source
        +str signal
    }

    class ValueOperand {
        +value
    }

    DSLFlowIR "1" *-- "1..*" FlowIR
    FlowIR "1" *-- "1..*" NodeIR
    FlowIR "1" *-- "0..*" EdgeIR
    FlowIR "1" o-- "0..1" EvaluationIR
    NodeIR "1" *-- "0..*" ActionIR
    EdgeIR "1" o-- "0..1" ComparisonCondition
    EdgeIR "1" o-- "0..1" TimeoutCondition
    EdgeIR "1" o-- "0..1" AnyOfCondition
    EdgeIR "1" o-- "0..1" AllOfCondition
    EdgeIR "1" o-- "0..1" NotCondition
    EdgeIR "1" *-- "0..*" ActionIR
    ComparisonCondition o-- SignalOperand
    ComparisonCondition o-- ValueOperand
    AnyOfCondition *-- ComparisonCondition
    AnyOfCondition *-- TimeoutCondition
    AllOfCondition *-- ComparisonCondition
    AllOfCondition *-- TimeoutCondition
    NotCondition o-- ComparisonCondition
    NotCondition o-- TimeoutCondition
```

---

## 4. クラス図 — Core モジュール

```mermaid
classDiagram
    class DSLParser {
        -jsonschema.Validator _validator
        +__init__(schema_path: Path)
        +parse(dsl_path: Path) DSLFlowIR
        +parse_dict(data: dict) DSLFlowIR
        -_validate_schema(data, source)
        -_build_ir(data) DSLFlowIR
        -_build_flow(data) FlowIR
        -_build_node(data) NodeIR
        -_build_edge(data) EdgeIR
        -_build_condition(data) Condition
        -_build_operand(data) Operand
        -_build_action(data) ActionIR
    }

    class ParseError {
    }

    class SemanticValidator {
        +validate(ir: DSLFlowIR) list~ValidationIssue~
        -_validate_flow(flow) list~ValidationIssue~
        -_check_duplicate_ids(ids, code, flow_id)
        -_check_start_end(flow)
        -_check_edge_refs(flow, node_ids)
        -_check_reachability(flow)
        -_check_cycles(flow)
        -_build_adjacency(flow) dict
    }

    class ValidationIssue {
        +str level
        +str code
        +str message
        +str flow_id
        +str node_id
        +str edge_id
        +__str__() str
    }

    class TypeChecker {
        +check(ir: DSLFlowIR) list~ValidationIssue~
        -_check_edge(flow_id, edge)
        -_check_condition(flow_id, edge_id, cond)
    }

    DSLParser ..> ParseError : raises
    DSLParser ..> DSLFlowIR : produces
    SemanticValidator ..> DSLFlowIR : reads
    SemanticValidator ..> ValidationIssue : produces
    TypeChecker ..> DSLFlowIR : reads
    TypeChecker ..> ValidationIssue : produces
```

---

## 5. Semantic Validator 検証ルール一覧

| コード | レベル | 検証内容 |
|---|---|---|
| `DUPLICATE_NODE_ID` | error | `node.id` の重複 |
| `DUPLICATE_EDGE_ID` | error | `edge.id` の重複 |
| `NO_START_NODE` | error | `start` node が存在しない |
| `MULTIPLE_START_NODES` | error | `start` node が複数存在する |
| `NO_END_NODE` | error | `end` node が存在しない |
| `INVALID_EDGE_SOURCE` | error | `edge.source` が存在しない node を参照している |
| `INVALID_EDGE_TARGET` | error | `edge.target` が存在しない node を参照している |
| `UNREACHABLE_NODE` | warning | `start` node から到達不能な node がある |
| `POSSIBLE_CYCLE` | warning | フロー内に循環（無限ループ）の可能性がある |

error がある場合、到達性・循環検出は実行しない（グラフが壊れているため）。

---

## 6. Type Checker 検証ルール一覧

| コード | レベル | 検証内容 |
|---|---|---|
| `INVALID_RESULT` | error | `edge.result` が許可値以外 |
| `INVALID_OPERATOR` | error | `comparison.operator` が許可値以外 |
| `INVALID_CLOCK` | error | `timeout.clock` が許可値以外 |
| `INVALID_UNIT` | error | `timeout.unit` が許可値以外 |

---

## 7. モジュール依存関係

```mermaid
graph TD
    parser[core.parser] --> ir[core.ir]
    semantic_validator[core.semantic_validator] --> ir
    type_checker[core.type_checker] --> ir
    type_checker --> semantic_validator
```

`type_checker` は `ValidationIssue` を `semantic_validator` から再利用している。  
`parser` / `semantic_validator` / `type_checker` は互いに依存しない。

---

## 8. ディレクトリ構成

```text
src/core/
├─ __init__.py
├─ ir/
│  ├─ __init__.py        # 公開 API エクスポート
│  └─ models.py          # IR データクラス定義
├─ parser/
│  ├─ __init__.py
│  └─ dsl_parser.py      # DSLParser / ParseError
├─ semantic_validator/
│  ├─ __init__.py
│  └─ validator.py       # SemanticValidator / ValidationIssue
└─ type_checker/
   ├─ __init__.py
   └─ checker.py         # TypeChecker

tests/core/
├─ test_parser.py        # 11 テスト
├─ test_semantic_validator.py  # 11 テスト
└─ test_type_checker.py  # 7 テスト
```
