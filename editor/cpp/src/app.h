#pragma once
#include "dsl_model.h"
#include <string>
#include <vector>
#include <optional>

namespace testflow {

class App {
public:
    App();
    ~App();

    void run();

private:
    void render_menu_bar();
    void render_graph_view();
    void render_property_panel();
    void render_validation_panel();

    void open_file_dialog();
    void save_file_dialog();
    void do_validate();

    DSLDocument doc_;
    std::vector<ValidationIssue> issues_;

    std::optional<std::string> selected_node_id_;
    std::optional<std::string> selected_edge_id_;

    bool show_validation_panel_{false};
};

}  // namespace testflow
