#include "graph_view.h"
#include <imgui.h>
#include <imgui_node_editor.h>
#include <unordered_map>
#include <cstdint>

namespace ed = ax::NodeEditor;

namespace testflow {

// ノードIDを文字列 ↔ uintptr_t で相互変換する簡易マッパー
// imgui-node-editor は整数 ID を要求する
struct IdMapper {
    std::unordered_map<std::string, uintptr_t> str_to_id;
    std::unordered_map<uintptr_t, std::string> id_to_str;
    uintptr_t next_id{1};

    uintptr_t get(const std::string& s) {
        auto it = str_to_id.find(s);
        if (it != str_to_id.end()) return it->second;
        uintptr_t id = next_id++;
        str_to_id[s] = id;
        id_to_str[id] = s;
        return id;
    }

    const std::string* find(uintptr_t id) const {
        auto it = id_to_str.find(id);
        return it != id_to_str.end() ? &it->second : nullptr;
    }
};

// グローバルコンテキスト（シングルフロー想定）
static ed::EditorContext* g_context = nullptr;
static IdMapper g_node_mapper;
static IdMapper g_edge_mapper;
// ピン ID: ノードごとに output pin と input pin を 2つ持つ
// output pin ID = node numeric ID * 2
// input  pin ID = node numeric ID * 2 + 1

GraphViewResult render_graph(DSLDocument& doc) {
    GraphViewResult result;
    if (doc.flows.empty()) return result;
    auto& flow = doc.flows[0];

    if (!g_context) {
        ed::Config cfg;
        g_context = ed::CreateEditor(&cfg);
    }

    ed::SetCurrentEditor(g_context);
    ed::Begin("TestFlow Graph", ImVec2(0, 0));

    // ---- Nodes ----
    for (auto& node : flow.nodes) {
        uintptr_t nid = g_node_mapper.get(node.id);
        ed::BeginNode(nid);

        // ノード種別ごとに色を変える
        if (node.type == "start")      ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.2f, 0.8f, 0.2f, 1.0f));
        else if (node.type == "end")   ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.8f, 0.2f, 0.2f, 1.0f));
        else                           ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.9f, 0.9f, 0.9f, 1.0f));

        ImGui::Text("[%s]", node.type.c_str());
        ImGui::SameLine();
        ImGui::Text("%s", node.id.c_str());
        ImGui::PopStyleColor();

        if (!node.description.empty())
            ImGui::TextWrapped("%s", node.description.c_str());

        // Input pin
        ed::BeginPin(nid * 2 + 1, ed::PinKind::Input);
        ImGui::Text(">");
        ed::EndPin();

        ImGui::SameLine();

        // Output pin
        ed::BeginPin(nid * 2, ed::PinKind::Output);
        ImGui::Text(">");
        ed::EndPin();

        ed::EndNode();

        // 初回のみ位置を設定する
        ed::SetNodePosition(nid, ImVec2(node.x, node.y));
    }

    // ---- Edges (Links) ----
    for (auto& edge : flow.edges) {
        uintptr_t eid       = g_edge_mapper.get(edge.id);
        uintptr_t src_pin   = g_node_mapper.get(edge.source) * 2;       // output
        uintptr_t tgt_pin   = g_node_mapper.get(edge.target) * 2 + 1;   // input
        ed::Link(eid, src_pin, tgt_pin);
    }

    // ---- Handle node dragging (position update) ----
    for (auto& node : flow.nodes) {
        uintptr_t nid = g_node_mapper.get(node.id);
        ImVec2 pos = ed::GetNodePosition(nid);
        if (pos.x != node.x || pos.y != node.y) {
            node.x = pos.x;
            node.y = pos.y;
            result.modified = true;
        }
    }

    // ---- Handle new link creation ----
    if (ed::BeginCreate()) {
        ed::PinId src_pin_id, tgt_pin_id;
        if (ed::QueryNewLink(&src_pin_id, &tgt_pin_id)) {
            if (ed::AcceptNewItem()) {
                // 新しい Edge を追加する（最小実装: condition なし）
                uintptr_t src_nid = (uintptr_t)src_pin_id / 2;
                uintptr_t tgt_nid = ((uintptr_t)tgt_pin_id - 1) / 2;
                const std::string* src = g_node_mapper.find(src_nid);
                const std::string* tgt = g_node_mapper.find(tgt_nid);
                if (src && tgt) {
                    Edge new_edge;
                    new_edge.id     = "edge_new_" + std::to_string(flow.edges.size() + 1);
                    new_edge.source = *src;
                    new_edge.target = *tgt;
                    flow.edges.push_back(new_edge);
                    result.modified = true;
                }
            }
        }
    }
    ed::EndCreate();

    // ---- Handle selection ----
    ed::NodeId selected_node_id;
    if (ed::GetSelectedNodes(&selected_node_id, 1) > 0) {
        const std::string* s = g_node_mapper.find((uintptr_t)selected_node_id);
        if (s) result.selected_node_id = *s;
    }

    ed::LinkId selected_edge_id;
    if (ed::GetSelectedLinks(&selected_edge_id, 1) > 0) {
        const std::string* s = g_edge_mapper.find((uintptr_t)selected_edge_id);
        if (s) result.selected_edge_id = *s;
    }

    ed::End();
    ed::SetCurrentEditor(nullptr);
    return result;
}

}  // namespace testflow
