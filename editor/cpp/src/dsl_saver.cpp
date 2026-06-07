#include "dsl_saver.h"
#include <nlohmann/json.hpp>
#include <fstream>

using json = nlohmann::json;

namespace testflow {

static json operand_to_json(const Operand& op) {
    return std::visit([](auto&& o) -> json {
        using T = std::decay_t<decltype(o)>;
        if constexpr (std::is_same_v<T, SignalOperand>) {
            return {{"source", o.source}, {"signal", o.signal}};
        } else {
            json v;
            std::visit([&v](auto&& val) {
                using V = std::decay_t<decltype(val)>;
                if constexpr (std::is_same_v<V, std::monostate>) v = nullptr;
                else v = val;
            }, o.value);
            return {{"value", v}};
        }
    }, op);
}

static json condition_to_json(const Condition& cond);

static json condition_to_json(const Condition& cond) {
    return std::visit([](auto&& c) -> json {
        using T = std::decay_t<decltype(c)>;
        if constexpr (std::is_same_v<T, ComparisonCondition>) {
            json j = {
                {"type", "comparison"},
                {"left",  operand_to_json(c.left)},
                {"operator", c.op},
                {"right", operand_to_json(c.right)}
            };
            if (c.unit) j["unit"] = *c.unit;
            return j;
        } else if constexpr (std::is_same_v<T, TimeoutCondition>) {
            return {{"type", "timeout"}, {"clock", c.clock}, {"value", c.value}, {"unit", c.unit}};
        } else if constexpr (std::is_same_v<T, AnyOfCondition>) {
            json subs = json::array();
            for (auto& sub : c.conditions) subs.push_back(condition_to_json(sub));
            return {{"type", "anyOf"}, {"conditions", subs}};
        } else if constexpr (std::is_same_v<T, AllOfCondition>) {
            json subs = json::array();
            for (auto& sub : c.conditions) subs.push_back(condition_to_json(sub));
            return {{"type", "allOf"}, {"conditions", subs}};
        } else {  // NotCondition
            return {{"type", "not"}, {"condition", condition_to_json(c.conditions[0])}};
        }
    }, cond);
}

static json action_to_json(const Action& a) {
    json j = {{"action", a.action}};
    if (a.signal)       j["signal"]      = *a.signal;
    if (a.value)        j["value"]       = json::parse(*a.value);
    if (a.processor)    j["processor"]   = *a.processor;
    if (a.apply_timing) j["applyTiming"] = *a.apply_timing;
    return j;
}

static json node_to_json(const Node& n) {
    json j = {{"id", n.id}, {"type", n.type}};
    if (!n.description.empty()) j["description"] = n.description;
    if (!n.entry_actions.empty()) {
        json acts = json::array();
        for (auto& a : n.entry_actions) acts.push_back(action_to_json(a));
        j["entryActions"] = acts;
    }
    j["ui"] = {{"x", n.x}, {"y", n.y}};
    return j;
}

static json edge_to_json(const Edge& e) {
    json j = {{"id", e.id}, {"source", e.source}, {"target", e.target}};
    if (e.condition) j["condition"] = condition_to_json(*e.condition);
    if (e.result)    j["result"]    = *e.result;
    if (e.priority != 0) j["priority"] = e.priority;
    if (!e.actions.empty()) {
        json acts = json::array();
        for (auto& a : e.actions) acts.push_back(action_to_json(a));
        j["actions"] = acts;
    }
    return j;
}

void save_dsl(const DSLDocument& doc, const std::string& path) {
    json root;
    root["dslVersion"] = doc.dsl_version;
    root["flows"] = json::array();

    for (auto& flow : doc.flows) {
        json jf;
        jf["id"]          = flow.id;
        jf["name"]        = flow.name;
        jf["description"] = flow.description;
        jf["startNodeId"] = flow.start_node_id;

        jf["nodes"] = json::array();
        for (auto& n : flow.nodes) jf["nodes"].push_back(node_to_json(n));

        jf["edges"] = json::array();
        for (auto& e : flow.edges) jf["edges"].push_back(edge_to_json(e));

        if (flow.evaluation) {
            json je = {{"enabled", flow.evaluation->enabled}};
            if (flow.evaluation->aggregation) je["aggregation"] = *flow.evaluation->aggregation;
            jf["evaluation"] = je;
        }
        root["flows"].push_back(jf);
    }

    std::ofstream f(path);
    if (!f) throw DSLSaveError("Cannot open file for writing: " + path);
    f << root.dump(2) << "\n";
}

}  // namespace testflow
