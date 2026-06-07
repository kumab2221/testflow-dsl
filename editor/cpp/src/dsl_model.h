#pragma once
#include <string>
#include <vector>
#include <optional>
#include <variant>

namespace testflow {

// --------------------------------------------------------------------------
// Operand
// --------------------------------------------------------------------------

struct SignalOperand {
    std::string source;  // backendInput / observed / internal / derived / reference / clock
    std::string signal;
};

struct ValueOperand {
    std::variant<std::monostate, bool, int64_t, double, std::string> value;
};

using Operand = std::variant<SignalOperand, ValueOperand>;

// --------------------------------------------------------------------------
// Condition (forward declaration for recursive types)
// --------------------------------------------------------------------------

struct ComparisonCondition;
struct TimeoutCondition;
struct AnyOfCondition;
struct AllOfCondition;
struct NotCondition;

using Condition = std::variant<
    ComparisonCondition,
    TimeoutCondition,
    AnyOfCondition,
    AllOfCondition,
    NotCondition
>;

struct ComparisonCondition {
    Operand left;
    std::string op;   // equals / notEquals / greaterThan / greaterThanOrEqual / lessThan / lessThanOrEqual
    Operand right;
    std::optional<std::string> unit;
};

struct TimeoutCondition {
    std::string clock;  // elapsedBlockSimulationTime / simulationTime / wallClockTime / sampleIndex
    double value;
    std::string unit;   // s / ms / us
};

struct AnyOfCondition  { std::vector<Condition> conditions; };
struct AllOfCondition  { std::vector<Condition> conditions; };
struct NotCondition    { std::vector<Condition> conditions; };  // single element

// --------------------------------------------------------------------------
// Action
// --------------------------------------------------------------------------

struct Action {
    std::string action;  // setBackendInput / setInternalSignal / callExternalProcessor
    std::optional<std::string> signal;
    std::optional<std::string> value;
    std::optional<std::string> processor;
    std::optional<std::string> apply_timing;
};

// --------------------------------------------------------------------------
// Edge
// --------------------------------------------------------------------------

struct Edge {
    std::string id;
    std::string source;
    std::string target;
    std::optional<Condition> condition;
    std::optional<std::string> result;  // PASS / FAIL / NOT_EVALUATED
    int priority{0};
    std::vector<Action> actions;
};

// --------------------------------------------------------------------------
// Node
// --------------------------------------------------------------------------

struct Node {
    std::string id;
    std::string type;   // start / block / end / condition / timer / action
    std::string description;
    std::vector<Action> entry_actions;

    // UI
    float x{0.0f};
    float y{0.0f};
};

// --------------------------------------------------------------------------
// Evaluation
// --------------------------------------------------------------------------

struct Evaluation {
    bool enabled{true};
    std::optional<std::string> aggregation;  // failIfAnyBlockFails / passIfAllBlocksPass
};

// --------------------------------------------------------------------------
// Flow
// --------------------------------------------------------------------------

struct Flow {
    std::string id;
    std::string name;
    std::string description;
    std::string start_node_id;
    std::vector<Node> nodes;
    std::vector<Edge> edges;
    std::optional<Evaluation> evaluation;
};

// --------------------------------------------------------------------------
// DSL document
// --------------------------------------------------------------------------

struct DSLDocument {
    std::string dsl_version;
    std::string ir_version;
    std::vector<Flow> flows;

    bool dirty{false};  // unsaved changes
    std::string file_path;
};

// --------------------------------------------------------------------------
// Validation issue
// --------------------------------------------------------------------------

struct ValidationIssue {
    std::string level;    // error / warning
    std::string code;
    std::string message;
    std::optional<std::string> flow_id;
    std::optional<std::string> node_id;
    std::optional<std::string> edge_id;
};

}  // namespace testflow
