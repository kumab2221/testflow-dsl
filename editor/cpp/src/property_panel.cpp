#include "property_panel.h"
#include <imgui.h>
#include <array>
#include <cstring>

namespace testflow {

static constexpr size_t BUF_SIZE = 512;

static void edit_node(DSLDocument& doc, const std::string& node_id) {
    if (doc.flows.empty()) return;
    auto& flow = doc.flows[0];

    Node* node = nullptr;
    for (auto& n : flow.nodes) if (n.id == node_id) { node = &n; break; }
    if (!node) return;

    ImGui::Text("Node: %s  (type: %s)", node->id.c_str(), node->type.c_str());
    ImGui::Separator();

    // description
    std::array<char, BUF_SIZE> buf{};
    std::strncpy(buf.data(), node->description.c_str(), BUF_SIZE - 1);
    ImGui::Text("description:");
    if (ImGui::InputTextMultiline("##desc", buf.data(), BUF_SIZE,
                                   ImVec2(-1, 80), ImGuiInputTextFlags_EnterReturnsTrue)) {
        node->description = buf.data();
        doc.dirty = true;
    }

    // entry_actions (MVP: 追加・削除のみ)
    ImGui::Separator();
    ImGui::Text("Entry Actions (%zu):", node->entry_actions.size());
    for (size_t i = 0; i < node->entry_actions.size(); ++i) {
        auto& a = node->entry_actions[i];
        ImGui::PushID(static_cast<int>(i));
        ImGui::Text("[%zu] %s", i, a.action.c_str());
        ImGui::SameLine();
        if (ImGui::SmallButton("x")) {
            node->entry_actions.erase(node->entry_actions.begin() + i);
            doc.dirty = true;
            ImGui::PopID();
            break;
        }
        ImGui::PopID();
    }

    if (ImGui::Button("+ Add Action")) {
        ImGui::OpenPopup("add_action_popup");
    }
    if (ImGui::BeginPopup("add_action_popup")) {
        const char* actions[] = {"setBackendInput", "setInternalSignal", "callExternalProcessor"};
        for (auto act : actions) {
            if (ImGui::MenuItem(act)) {
                Action a;
                a.action = act;
                node->entry_actions.push_back(std::move(a));
                doc.dirty = true;
            }
        }
        ImGui::EndPopup();
    }
}

static void edit_comparison_condition(ComparisonCondition& c, bool& dirty) {
    // operator
    const char* ops[] = {
        "equals", "notEquals", "greaterThan", "greaterThanOrEqual", "lessThan", "lessThanOrEqual"
    };
    int cur = 0;
    for (int i = 0; i < 6; ++i) if (c.op == ops[i]) { cur = i; break; }
    ImGui::Text("operator:");
    if (ImGui::Combo("##op", &cur, ops, 6)) {
        c.op = ops[cur];
        dirty = true;
    }

    // right operand (値の場合のみ簡易編集)
    if (auto* v = std::get_if<ValueOperand>(&c.right)) {
        std::array<char, 64> buf{};
        if (auto* d = std::get_if<double>(&v->value)) {
            std::snprintf(buf.data(), 64, "%.4g", *d);
        } else if (auto* i = std::get_if<int64_t>(&v->value)) {
            std::snprintf(buf.data(), 64, "%lld", (long long)*i);
        } else if (auto* s = std::get_if<std::string>(&v->value)) {
            std::strncpy(buf.data(), s->c_str(), 63);
        }
        ImGui::Text("right value:");
        if (ImGui::InputText("##right", buf.data(), 64)) {
            v->value = std::string(buf.data());
            dirty = true;
        }
    } else {
        ImGui::Text("right: (signal operand)");
    }
}

static void edit_timeout_condition(TimeoutCondition& c, bool& dirty) {
    ImGui::Text("clock: %s", c.clock.c_str());
    float val = static_cast<float>(c.value);
    ImGui::Text("value:");
    if (ImGui::InputFloat("##val", &val, 1.0f, 10.0f, "%.1f")) {
        c.value = val;
        dirty = true;
    }
    const char* units[] = {"s", "ms", "us"};
    int cur = 0;
    for (int i = 0; i < 3; ++i) if (c.unit == units[i]) { cur = i; break; }
    ImGui::Text("unit:");
    if (ImGui::Combo("##unit", &cur, units, 3)) {
        c.unit = units[cur];
        dirty = true;
    }
}

static void edit_condition(Condition& cond, bool& dirty) {
    std::visit([&dirty](auto&& c) {
        using T = std::decay_t<decltype(c)>;
        if constexpr (std::is_same_v<T, ComparisonCondition>) {
            ImGui::Text("Type: comparison");
            edit_comparison_condition(c, dirty);
        } else if constexpr (std::is_same_v<T, TimeoutCondition>) {
            ImGui::Text("Type: timeout");
            edit_timeout_condition(c, dirty);
        } else {
            ImGui::Text("Type: composite (anyOf/allOf/not) — edit in JSON");
        }
    }, cond);
}

static void edit_edge(DSLDocument& doc, const std::string& edge_id) {
    if (doc.flows.empty()) return;
    auto& flow = doc.flows[0];

    Edge* edge = nullptr;
    for (auto& e : flow.edges) if (e.id == edge_id) { edge = &e; break; }
    if (!edge) return;

    ImGui::Text("Edge: %s", edge->id.c_str());
    ImGui::Text("  %s → %s", edge->source.c_str(), edge->target.c_str());
    ImGui::Separator();

    // result
    const char* results[] = {"(none)", "PASS", "FAIL", "NOT_EVALUATED"};
    int cur = 0;
    if (edge->result) {
        for (int i = 1; i < 4; ++i) if (*edge->result == results[i]) { cur = i; break; }
    }
    ImGui::Text("result:");
    if (ImGui::Combo("##result", &cur, results, 4)) {
        edge->result = (cur == 0) ? std::nullopt : std::optional<std::string>(results[cur]);
        doc.dirty = true;
    }

    // priority
    int prio = edge->priority;
    ImGui::Text("priority:");
    if (ImGui::InputInt("##prio", &prio)) {
        edge->priority = prio;
        doc.dirty = true;
    }

    // condition
    ImGui::Separator();
    if (edge->condition) {
        ImGui::Text("Condition:");
        bool dirty = false;
        edit_condition(*edge->condition, dirty);
        if (dirty) doc.dirty = true;
    } else {
        ImGui::Text("Condition: (none)");
    }
}

void render_property_panel(
    DSLDocument& doc,
    const std::optional<std::string>& selected_node_id,
    const std::optional<std::string>& selected_edge_id
) {
    ImGui::Begin("Properties");

    if (selected_node_id) {
        edit_node(doc, *selected_node_id);
    } else if (selected_edge_id) {
        edit_edge(doc, *selected_edge_id);
    } else {
        ImGui::Text("(nothing selected)");
    }

    ImGui::End();
}

}  // namespace testflow
