#pragma once
#include "dsl_model.h"
#include <optional>
#include <string>

namespace testflow {

// 選択中の node / edge のプロパティ編集パネルを描画する。
// 変更があった場合は doc.dirty = true にする。
void render_property_panel(
    DSLDocument& doc,
    const std::optional<std::string>& selected_node_id,
    const std::optional<std::string>& selected_edge_id
);

}  // namespace testflow
