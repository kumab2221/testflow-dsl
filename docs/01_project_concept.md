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
作成物

```text
Test Logic DSL + NodeEditor + Multiple Backends
```

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

## 4. やらないこと

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
