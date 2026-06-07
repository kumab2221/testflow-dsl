#include "dsl_loader.h"
#include <nlohmann/json.hpp>
#include <fstream>

using json = nlohmann::json;

namespace testflow {

static Operand parse_operand(const json& j) {
    if (j.contains("source")) {
        return SignalOperand{j.at("source").get<std::string>(), j.at("signal").get<std::string>()};
    }
    ValueOperand v;
    auto& val = j.at("value");
    if (val.is_boolean())     v.value = val.get<bool>();
    else if (val.is_number_integer()) v.value = val.get<int64_t>();
    else if (val.is_number_float())   v.value = val.get<double>();
    else if (val.is_string())         v.value = val.get<std::string>();
    return v;
}

static Condition parse_condition(const json& j);

static Condition parse_condition(const json& j) {
    std::string type = j.at("type").get<std::string>();

    if (type == "comparison") {
        ComparisonCondition c;
        c.left  = parse_operand(j.at("left"));
        c.op    = j.at("operator").get<std::string>();
        c.right = parse_operand(j.at("right"));
        if (j.contains("unit")) c.unit = j.at("unit").get<std::string>();
        return c;
    }
    if (type == "timeout") {
        return TimeoutCondition{
            j.at("clock").get<std::string>(),
            j.at("value").get<double>(),
            j.at("unit").get<std::string>()
        };
    }
    if (type == "anyOf") {
        AnyOfCondition c;
        for (auto& sub : j.at("conditions")) c.conditions.push_back(parse_condition(sub));
        return c;
    }
    if (type == "allOf") {
        AllOfCondition c;
        for (auto& sub : j.at("conditions")) c.conditions.push_back(parse_condition(sub));
        return c;
    }
    if (type == "not") {
        NotCondition c;
        c.conditions.push_back(parse_condition(j.at("condition")));
        return c;
    }
    throw DSLLoadError("Unknown condition type: " + type);
}

static Action parse_action(const json& j) {
    Action a;
    a.action = j.at("action").get<std::string>();
    if (j.contains("signal"))       a.signal       = j.at("signal").get<std::string>();
    if (j.contains("value"))        a.value        = j.at("value").dump();
    if (j.contains("processor"))    a.processor    = j.at("processor").get<std::string>();
    if (j.contains("applyTiming"))  a.apply_timing = j.at("applyTiming").get<std::string>();
    return a;
}

static Node parse_node(const json& j) {
    Node n;
    n.id   = j.at("id").get<std::string>();
    n.type = j.at("type").get<std::string>();
    if (j.contains("description")) n.description = j.at("description").get<std::string>();
    if (j.contains("entryActions"))
        for (auto& a : j.at("entryActions")) n.entry_actions.push_back(parse_action(a));
    if (j.contains("ui")) {
        auto& ui = j.at("ui");
        if (ui.contains("x")) n.x = ui.at("x").get<float>();
        if (ui.contains("y")) n.y = ui.at("y").get<float>();
    }
    return n;
}

static Edge parse_edge(const json& j) {
    Edge e;
    e.id     = j.at("id").get<std::string>();
    e.source = j.at("source").get<std::string>();
    e.target = j.at("target").get<std::string>();
    if (j.contains("condition")) e.condition = parse_condition(j.at("condition"));
    if (j.contains("result"))    e.result    = j.at("result").get<std::string>();
    if (j.contains("priority"))  e.priority  = j.at("priority").get<int>();
    if (j.contains("actions"))
        for (auto& a : j.at("actions")) e.actions.push_back(parse_action(a));
    return e;
}

DSLDocument load_dsl(const std::string& path) {
    std::ifstream f(path);
    if (!f) throw DSLLoadError("Cannot open file: " + path);

    json root;
    try { root = json::parse(f); }
    catch (const json::exception& ex) { throw DSLLoadError(ex.what()); }

    DSLDocument doc;
    doc.file_path  = path;
    doc.dsl_version = root.value("dslVersion", "");
    doc.ir_version  = root.value("irVersion", "");

    for (auto& jf : root.at("flows")) {
        Flow flow;
        flow.id          = jf.at("id").get<std::string>();
        flow.name        = jf.at("name").get<std::string>();
        flow.description = jf.value("description", "");
        flow.start_node_id = jf.at("startNodeId").get<std::string>();

        for (auto& jn : jf.at("nodes")) flow.nodes.push_back(parse_node(jn));
        for (auto& je : jf.at("edges")) flow.edges.push_back(parse_edge(je));

        if (jf.contains("evaluation")) {
            auto& je = jf.at("evaluation");
            Evaluation ev;
            ev.enabled = je.value("enabled", true);
            if (je.contains("aggregation")) ev.aggregation = je.at("aggregation").get<std::string>();
            flow.evaluation = ev;
        }
        doc.flows.push_back(std::move(flow));
    }

    return doc;
}

}  // namespace testflow
