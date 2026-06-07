# 05. Backend Strategy

## 1. 方針

Backend は TestFlow IR を受け取り、各実行環境に合わせて compile / run / result export を行う。

DSL は特定バックエンドに依存させない。

## 2. Backendの種類

初期候補：

```text
- Python Runtime Backend
- OpenTAP Backend
- MATLAB / Simulink Backend
- C++ Backend
- UE Backend
- HILS Backend
```

## 3. 最初のBackend

最初は Python Runtime Backend とする。

理由：

```text
- 実装が早い
- pytestで検証しやすい
- JSON / CSV / 時系列処理と相性が良い
- DSLの意味論を検証しやすい
- OpenTAPやMATLABに依存しない
```

## 4. Backend Capability

Backendは対応機能を宣言する。

```json
{
  "backend": "python-runtime",
  "version": "0.1.0",
  "capabilities": {
    "sequence": true,
    "parallel": false,
    "nestedParallel": false,
    "comparisonCondition": true,
    "timeoutCondition": true,
    "simulationTime": true,
    "runtimeFeedback": true,
    "externalProcessor": true
  }
}
```

## 5. Capability Validation

Runtime実行前に、IRがBackendで実行可能か検証する。

例：

```text
DSLで parallel を使用している
↓
Python Runtime Backend capabilities.parallel = false
↓
実行前エラー
```

## 6. Backend Interface

```text
getCapabilities() -> BackendCapabilities
validateCapabilities(ir) -> ValidationResult
compile(ir) -> CompiledPlan
run(compiledPlan) -> ExecutionResult
collectResults() -> ResultLog
exportResult(format) -> file
```

## 7. Backendを増やす順番

推奨順：

```text
1. Python Runtime
2. C++ Backend
3. OpenTAP Backend
4. External Tool Backend
5. MATLAB / Simulink Backend
6. UE / HILS Backend
```
