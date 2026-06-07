#include "validator_runner.h"
#include <nlohmann/json.hpp>
#include <array>
#include <cstdio>
#include <stdexcept>
#include <string>

using json = nlohmann::json;

namespace testflow {

static std::string exec_command(const std::string& cmd) {
    std::array<char, 256> buf;
    std::string result;
#ifdef _WIN32
    FILE* pipe = _popen(cmd.c_str(), "r");
#else
    FILE* pipe = popen(cmd.c_str(), "r");
#endif
    if (!pipe) return "";
    while (fgets(buf.data(), buf.size(), pipe) != nullptr) result += buf.data();
#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    return result;
}

std::vector<ValidationIssue> run_validator(
    const std::string& json_path,
    const std::string& python_executable
) {
    // validator_cli.py --json-output <path> を呼び出す
    std::string cmd = python_executable + " -m testflow_validator --json-output \"" + json_path + "\" 2>&1";
    std::string output = exec_command(cmd);

    std::vector<ValidationIssue> issues;
    if (output.empty()) return issues;

    try {
        auto jarr = json::parse(output);
        for (auto& ji : jarr) {
            ValidationIssue issue;
            issue.level   = ji.value("level", "error");
            issue.code    = ji.value("code", "");
            issue.message = ji.value("message", "");
            if (ji.contains("flowId"))  issue.flow_id = ji.at("flowId").get<std::string>();
            if (ji.contains("nodeId"))  issue.node_id = ji.at("nodeId").get<std::string>();
            if (ji.contains("edgeId"))  issue.edge_id = ji.at("edgeId").get<std::string>();
            issues.push_back(std::move(issue));
        }
    } catch (...) {
        // JSON パース失敗 → raw メッセージとして返す
        ValidationIssue issue;
        issue.level   = "error";
        issue.code    = "VALIDATOR_OUTPUT_ERROR";
        issue.message = output;
        issues.push_back(std::move(issue));
    }
    return issues;
}

}  // namespace testflow
