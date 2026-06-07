# 03. Architecture: NodeEditor + JSON DSL + Multiple Backends

## 1. 全体構成

```text
NodeEditor
   ↓
JSON DSL
   ↓
Parser
   ↓
Semantic Validator
   ↓
IR
   ↓
Backend Adapter
   ├─ Python Runtime
   ├─ OpenTAP Backend
   ├─ MATLAB / Simulink Backend
   ├─ UE Backend
   └─ HILS / External Tool Backend
```

## 2. 各層の責務

| 層                 | 責務                                       |
| ------------------ | ------------------------------------------ |
| NodeEditor         | DSLを視覚的に編集する                      |
| JSON DSL           | 保存形式、Git管理対象                      |
| JSON Schema        | 構文レベルの検証                           |
| Parser             | JSON DSLを内部モデルへ変換する             |
| Semantic Validator | 信号参照、型、接続、到達性、競合を検証する |
| IR                 | Backend非依存の中間表現                    |
| Backend Adapter    | IRを各実行環境へ変換・実行する             |
| Result Logger      | 共通結果ログを出力する                     |

## 3. JSONを直接実行しない理由

JSONを直接実行すると以下が問題になる。

```text
- UI情報と実行意味論が混ざる
- Backendごとの差分吸収が難しい
- バージョン移行が難しい
- 最適化や静的検証がしづらい
- NodeEditor都合の変更がRuntimeに波及する
```

そのため、必ず IR を挟む。

## 4. Backend Interface

各バックエンドは以下のインターフェースを持つ。

```text
Backend
├─ getCapabilities()
├─ validateCapabilities(ir)
├─ compile(ir)
├─ run(compiledPlan)
├─ collectResults()
└─ exportResult()
```

## 5. Capability宣言

Backend は対応機能を宣言する。

```json
{
  "backend": "python-runtime",
  "capabilities": {
    "sequence": true,
    "parallel": false,
    "nestedParallel": false,
    "simulationTime": true,
    "runtimeFeedback": true,
    "externalProcessor": true
  }
}
```

## 6. NodeEditorの役割

NodeEditor は DSL を作るためのUIであり、実行エンジンではない。

NodeEditor MVP で必要な機能：

```text
- ノード追加
- エッジ接続
- 条件編集
- JSON出力
- JSON読込
- Schema検証結果表示
- Semantic検証結果表示
```

高度な機能は後回しにする。

```text
- デバッグ実行
- 波形プレビュー
- バックエンド別サポート表示
- 自動レイアウト
- 履歴管理
```

