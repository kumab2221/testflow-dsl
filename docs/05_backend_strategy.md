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

## 4. OpenTAP Backendの位置づけ

OpenTAPは強力な実行基盤であるため、v0.2以降でBackend候補として評価する。

ただし、以下はAdapterまたはPluginが必要になる。

```text
- simulationTime
- elapsedBlockSimulationTime
- signalProcessing
- runtimeFeedback
- 共通Result Logへの変換
```

## 5. Backend Capability

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

## 6. Capability Validation

Runtime実行前に、IRがBackendで実行可能か検証する。

例：

```text
DSLで parallel を使用している
↓
Python Runtime Backend capabilities.parallel = false
↓
実行前エラー
```

## 7. Backend Interface

```text
getCapabilities() -> BackendCapabilities
validateCapabilities(ir) -> ValidationResult
compile(ir) -> CompiledPlan
run(compiledPlan) -> ExecutionResult
collectResults() -> ResultLog
exportResult(format) -> file
```

## 8. Backendを増やす順番

推奨順：

```text
1. Python Runtime
2. OpenTAP Backend評価
3. External Tool Backend
4. C++ Backend
5. MATLAB / Simulink Backend
6. UE / HILS Backend
```

OpenTAPを早く評価すべき理由は、v0.2のnested parallelを自作する前に、既存実行基盤でどこまで吸収できるか判断するためである。
