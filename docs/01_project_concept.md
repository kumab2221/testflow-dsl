# 01. Project Concept

## 1. 目的

`testflow-dsl` の目的は、テストロジックを特定ツールに依存せずに記述し、NodeEditor で安全に編集し、複数バックエンドで実行できるようにすることである。
対象は、手動テストではなく、自動実行可能なテストロジックである。
想定対象は以下である。

```text
- Python Runtime
- C++ Runtime
- OpenTAP
- MATLAB / Simulink
- UE
- HILS / SILS / MILS
- 外部シミュレーション環境
```

## 2. 方針転換

旧方針は「テストケースJSONを管理し、使用ツールと編集ツールを作る」だった。
新方針は以下である。
```text
Test Logic DSL + NodeEditor + Multiple Backends
```
これは単なる JSON 管理ツールではない。小さなテストロジック言語と、その編集・検証・実行基盤を作る方針である。

## 3. 本プロジェクトが解く問題

従来の課題は以下である。

```text
- MATLAB/Simulink 前提のテストツールはバージョン依存が強い
- OpenTAP 等の既存実行基盤は強力だが、時系列・信号処理・simulationTime 条件を社内仕様として直接表現しづらい
- JSON手書きでは条件・遷移・並列が複雑化し、壊れた仕様を作りやすい
- テストロジックを Git 管理し、レビューし、複数環境で実行したい
```

本プロジェクトは、これらを解くために以下を提供する。

```text
- TestFlow DSL
- NodeEditor
- JSON Schema
- Semantic Validator
- IR
- Backend Adapter
- 共通 Result Log
```

## 4. OpenTAPとの住み分け

OpenTAP は実行基盤として強い。プラグイン、テストステップ、シーケンス、結果収集などを持つ。

一方で、`testflow-dsl` は以下を主担当とする。

```text
- ツール非依存のテストロジック表現
- signalProcessing
- simulationTime / elapsedBlockSimulationTime
- runtimeFeedback
- NodeEditor によるロジック作成
- Backend 非依存の IR
```

したがって住み分けは以下である。

```text
testflow-dsl:
  テストロジックDSL、NodeEditor、IR、共通仕様

OpenTAP:
  実行バックエンド候補、機器制御、プラグイン、結果収集
```

## 5. やらないこと

初期段階では以下をやらない。

```text
- 完成度の高いGUIエディタ
- すべてのバックエンド対応
- 複雑な汎用プログラミング言語化
- 自由記述の自然言語条件の実行
- 単位自動変換
- 高度な最適化
```

まず、DSL Core、IR、Python Runtime PoC を成立させる。
