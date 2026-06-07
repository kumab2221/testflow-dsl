#pragma once
#include "dsl_model.h"
#include <string>
#include <stdexcept>

namespace testflow {

class DSLLoadError : public std::runtime_error {
public:
    explicit DSLLoadError(const std::string& msg) : std::runtime_error(msg) {}
};

DSLDocument load_dsl(const std::string& path);

}  // namespace testflow
