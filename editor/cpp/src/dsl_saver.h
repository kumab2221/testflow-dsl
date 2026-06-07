#pragma once
#include "dsl_model.h"
#include <string>
#include <stdexcept>

namespace testflow {

class DSLSaveError : public std::runtime_error {
public:
    explicit DSLSaveError(const std::string& msg) : std::runtime_error(msg) {}
};

void save_dsl(const DSLDocument& doc, const std::string& path);

}  // namespace testflow
