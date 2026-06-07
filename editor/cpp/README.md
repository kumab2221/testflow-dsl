# TestFlow Editor — C++ + Dear ImGui spike

spike ブランチ: `spike/editor-cpp-imgui-crossplatform`

## 依存関係

### Ubuntu

```bash
sudo apt install -y build-essential cmake libglfw3-dev libgl-dev zenity
```

Noto CJK フォント（日本語表示用）:

```bash
sudo apt install -y fonts-noto-cjk
```

### Windows

- Visual Studio 2022 (MSVC) または MinGW-w64
- CMake 3.20+
- GLFW は FetchContent で自動取得

## ビルド

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

## 実行

```bash
./build/testflow_editor
```

File → Open で `examples/simple_speed_flow.json` を開く。

## アーキテクチャ

```text
main.cpp          エントリポイント
app.cpp/.h        アプリ全体の管理・ウィンドウループ
graph_view.cpp/.h imgui-node-editor によるグラフ描画
property_panel.cpp/.h 選択ノード・エッジのプロパティ編集
dsl_loader.cpp/.h JSON DSL → DSLDocument
dsl_saver.cpp/.h  DSLDocument → JSON DSL
validator_runner.cpp/.h Python validator を外部実行
dsl_model.h       DSLDocument / Node / Edge / Condition などのデータモデル
```

## MVP 進捗

| ID | 内容 | 状態 |
|---|---|---|
| MVP-01 | simple_speed_flow.json を読み込む | 実装済 |
| MVP-02 | StartNode / BlockNode / EndNode を表示する | 実装済 |
| MVP-03 | ノードを移動できる | 実装済 |
| MVP-04 | Edge を接続できる | 実装済 |
| MVP-05 | BlockNode の description を編集できる | 実装済 |
| MVP-06 | Edge の condition を編集できる | 実装済（comparison/timeout） |
| MVP-07 | Action を選択できる | 実装済 |
| MVP-08 | JSON として保存できる | 実装済 |
| MVP-09 | Validator を呼び出しエラーを表示できる | 実装済（外部実行） |
| MVP-10 | 日本語 description を保存・再読込できる | 要実機確認 |
| MVP-11 | Ubuntu と Windows の両方で起動できる | 要実機確認 |

## 確認が必要な事項

- [ ] Ubuntu でビルドできるか
- [ ] Ubuntu で起動できるか（X11 / Wayland）
- [ ] 日本語フォント表示
- [ ] 日本語 IME 入力
- [ ] HiDPI
- [ ] zenity ファイルダイアログ
