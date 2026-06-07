// Tauri アプリのエントリポイント
// v0.1: ファイルI/O・ダイアログ・外部コマンド実行は Tauri plugin に委譲する
// DSL の parse / validate は TypeScript 側 (Ajv) または Python 外部実行で行う

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
