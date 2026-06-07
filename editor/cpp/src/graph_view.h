#pragma once
#include "dsl_model.h"
#include <optional>
#include <string>

namespace testflow {

struct GraphViewResult {
    std::optional<std::string> selected_node_id;
    std::optional<std::string> selected_edge_id;
    bool modified{false};
};

// ImGui + imgui-node-editor でグラフを描画する。
// doc の nodes / edges を NodeEditor のノード / リンクとして表示する。
// ノード移動・Edge接続操作の結果を doc に書き戻し、modified=true を返す。
GraphViewResult render_graph(DSLDocument& doc);

}  // namespace testflow
