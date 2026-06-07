#pragma once
#include "dsl_model.h"
#include <string>
#include <vector>

namespace testflow {

// Python validator を外部プロセスとして呼び出す。
// python3 -m core.semantic_validator ... を実行し、結果をパースする。
std::vector<ValidationIssue> run_validator(
    const std::string& json_path,
    const std::string& python_executable = "python3"
);

}  // namespace testflow
