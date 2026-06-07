# TestFlow Editor — Rust + Tauri + React Flow spike

spike ブランチ: `spike/editor-rust-tauri-crossplatform`

## 依存関係

### Ubuntu

```bash
# Tauri の Linux 依存
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Node.js (nvm 推奨)
npm install -g pnpm
```

### Windows

- Visual Studio 2022 Build Tools (MSVC)
- Rust (rustup)
- Node.js 20+

## セットアップ

```bash
cd editor/tauri
npm install
```

## 開発

```bash
npm run tauri dev
```

## ビルド

```bash
npm run tauri build
```

## アーキテクチャ

```text
src/
  main.tsx            エントリポイント
  App.tsx             レイアウト・DSLContext Provider
  store/
    dslStore.ts       DSLDocument の状態管理 (useReducer)
  types/
    dsl.ts            TypeScript 型定義（schema に準拠）
  components/
    MenuBar.tsx       Open / Save / Validate ボタン
    GraphView.tsx     React Flow グラフ描画
    PropertyPanel.tsx 選択ノード・エッジの編集フォーム
    ValidationPanel.tsx バリデーション結果表示
    nodes/
      StartNode.tsx
      BlockNode.tsx
      EndNode.tsx

src-tauri/
  src/
    lib.rs            Tauri アプリ初期化
    main.rs           エントリポイント
  tauri.conf.json     Tauri 設定
  Cargo.toml
```

## MVP 進捗

| ID | 内容 | 状態 |
|---|---|---|
| MVP-01 | simple_speed_flow.json を読み込む | 実装済 |
| MVP-02 | StartNode / BlockNode / EndNode を表示する | 実装済 |
| MVP-03 | ノードを移動できる | 実装済 |
| MVP-04 | Edge を接続できる | 実装済 |
| MVP-05 | BlockNode の description を編集できる | 実装済 |
| MVP-06 | Edge の condition を編集できる | 実装済（サマリ表示） |
| MVP-07 | Action を選択できる | 実装済 |
| MVP-08 | JSON として保存できる | 実装済 |
| MVP-09 | Validator を呼び出しエラーを表示できる | 実装済（外部実行） |
| MVP-10 | 日本語 description を保存・再読込できる | 要実機確認 |
| MVP-11 | Ubuntu と Windows の両方で起動できる | 要実機確認 |

## 確認が必要な事項

- [ ] Ubuntu で `npm run tauri dev` が通るか
- [ ] WebKitGTK の依存が問題ないか
- [ ] 日本語入力ができるか（IBus / Fcitx5）
- [ ] ファイルダイアログが開くか
- [ ] AppImage / deb 形式でのビルドが通るか
- [ ] Windows でのビルドが通るか
