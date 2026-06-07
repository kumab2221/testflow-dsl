# 08. Validation Strategy

## 1. 検証は3層に分ける

```text
1. JSON Schema Validation
2. Semantic Validation
3. Backend Capability Validation
```

## 2. JSON Schema Validation

検証対象：

```text
- JSON構造
- 必須項目
- 型
- enum
- additionalProperties
```

JSON Schemaは構文チェックであり、参照整合性までは十分に検証できない。

## 3. Semantic Validation

検証対象：

```text
- node.id の重複
- edge.id の重複
- edge.source / edge.target が存在すること
- start node が1つ以上存在すること
- end node が存在すること
- 到達不能node
- transitionが存在しないblock
- 複数edgeが同時成立する場合のpriority/解決方針
- conditionのsignal参照
- unitの不一致
- timeout clockの妥当性
```

## 4. Backend Capability Validation

検証対象：

```text
- DSLで使っている機能をBackendが対応しているか
- parallel未対応Backendでparallelを使っていないか
- simulationTimeをBackendが提供できるか
- runtimeFeedbackがBackendで実行可能か
- externalProcessorが対象環境で実行可能か
```

## 5. NodeEditorでのリアルタイム検証

NodeEditorでは保存前に以下を表示する。

```text
- Schema Error
- Semantic Error
- Backend Unsupported Feature
- Warning
```

## 6. Error / Warning の分類

| 分類          | 意味                    | 保存 | 実行 |
| ------------- | ----------------------- | ---: | ---: |
| Error         | DSLとして成立しない     | 不可 | 不可 |
| Warning       | 実行は可能だが危険      |   可 |   可 |
| Backend Error | 指定Backendでは実行不可 |   可 | 不可 |
| Info          | 補足情報                |   可 |   可 |

## 7. 重要な検証ルール

```text
- UI情報は実行意味論に影響しないこと
- JSON Schema の default に依存しないこと
- 暗黙挙動を避けること
- evaluation.enabled=falseでもflow遷移は評価されること
- Backendごとに実行可能性を明示すること
```
