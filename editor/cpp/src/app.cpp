#include "app.h"
#include "dsl_loader.h"
#include "dsl_saver.h"
#include "graph_view.h"
#include "property_panel.h"
#include "validator_runner.h"

#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>
#include <cstdio>
#include <string>

namespace testflow {

// ファイルダイアログの簡易実装（zenity / PowerShell を外部実行）
static std::string simple_open_dialog() {
#ifdef _WIN32
    // PowerShell で OpenFileDialog
    FILE* pipe = _popen(
        "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms;"
        "[System.Windows.Forms.OpenFileDialog]$d = New-Object System.Windows.Forms.OpenFileDialog;"
        "$d.Filter='JSON Files (*.json)|*.json|All Files (*.*)|*.*';"
        "if($d.ShowDialog() -eq 'OK'){$d.FileName}\"",
        "r"
    );
    if (!pipe) return "";
    char buf[1024] = {};
    fgets(buf, sizeof(buf), pipe);
    _pclose(pipe);
    std::string s(buf);
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
    return s;
#else
    // zenity
    FILE* pipe = popen("zenity --file-selection --file-filter='*.json' 2>/dev/null", "r");
    if (!pipe) return "";
    char buf[1024] = {};
    fgets(buf, sizeof(buf), pipe);
    pclose(pipe);
    std::string s(buf);
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
    return s;
#endif
}

static std::string simple_save_dialog(const std::string& default_path) {
#ifdef _WIN32
    FILE* pipe = _popen(
        "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms;"
        "[System.Windows.Forms.SaveFileDialog]$d = New-Object System.Windows.Forms.SaveFileDialog;"
        "$d.Filter='JSON Files (*.json)|*.json';"
        "if($d.ShowDialog() -eq 'OK'){$d.FileName}\"",
        "r"
    );
    if (!pipe) return default_path;
    char buf[1024] = {};
    fgets(buf, sizeof(buf), pipe);
    _pclose(pipe);
    std::string s(buf);
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
    return s.empty() ? default_path : s;
#else
    std::string cmd = "zenity --file-selection --save --filename='" + default_path + "' --file-filter='*.json' 2>/dev/null";
    FILE* pipe = popen(cmd.c_str(), "r");
    if (!pipe) return default_path;
    char buf[1024] = {};
    fgets(buf, sizeof(buf), pipe);
    pclose(pipe);
    std::string s(buf);
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
    return s.empty() ? default_path : s;
#endif
}

App::App() = default;
App::~App() = default;

void App::render_menu_bar() {
    if (ImGui::BeginMenuBar()) {
        if (ImGui::BeginMenu("File")) {
            if (ImGui::MenuItem("Open...", "Ctrl+O"))  open_file_dialog();
            if (ImGui::MenuItem("Save",    "Ctrl+S") && !doc_.file_path.empty())
                save_dsl(doc_, doc_.file_path);
            if (ImGui::MenuItem("Save As..."))          save_file_dialog();
            ImGui::Separator();
            if (ImGui::MenuItem("Validate", "Ctrl+Shift+V")) do_validate();
            ImGui::EndMenu();
        }
        if (ImGui::BeginMenu("View")) {
            ImGui::MenuItem("Validation Panel", nullptr, &show_validation_panel_);
            ImGui::EndMenu();
        }
        ImGui::EndMenuBar();
    }
}

void App::render_graph_view() {
    ImGui::Begin("Graph", nullptr, ImGuiWindowFlags_NoCollapse);
    auto res = render_graph(doc_);
    if (res.selected_node_id) selected_node_id_ = res.selected_node_id;
    if (res.selected_edge_id) selected_edge_id_ = res.selected_edge_id;
    if (res.modified) doc_.dirty = true;
    ImGui::End();
}

void App::render_property_panel() {
    testflow::render_property_panel(doc_, selected_node_id_, selected_edge_id_);
}

void App::render_validation_panel() {
    if (!show_validation_panel_) return;
    ImGui::Begin("Validation", &show_validation_panel_);
    if (issues_.empty()) {
        ImGui::TextColored(ImVec4(0.2f, 0.8f, 0.2f, 1.0f), "No issues.");
    } else {
        for (auto& issue : issues_) {
            ImVec4 color = (issue.level == "error")
                ? ImVec4(1.0f, 0.3f, 0.3f, 1.0f)
                : ImVec4(1.0f, 0.8f, 0.2f, 1.0f);
            ImGui::TextColored(color, "[%s] %s: %s",
                issue.level.c_str(), issue.code.c_str(), issue.message.c_str());
        }
    }
    ImGui::End();
}

void App::open_file_dialog() {
    std::string path = simple_open_dialog();
    if (path.empty()) return;
    try {
        doc_ = load_dsl(path);
        selected_node_id_.reset();
        selected_edge_id_.reset();
        issues_.clear();
    } catch (const std::exception& ex) {
        // TODO: エラーダイアログ
        fprintf(stderr, "Load error: %s\n", ex.what());
    }
}

void App::save_file_dialog() {
    std::string path = simple_save_dialog(doc_.file_path);
    if (path.empty()) return;
    try {
        save_dsl(doc_, path);
        doc_.file_path = path;
        doc_.dirty = false;
    } catch (const std::exception& ex) {
        fprintf(stderr, "Save error: %s\n", ex.what());
    }
}

void App::do_validate() {
    if (doc_.file_path.empty()) {
        save_file_dialog();
        if (doc_.file_path.empty()) return;
    }
    issues_ = run_validator(doc_.file_path);
    show_validation_panel_ = true;
}

void App::run() {
    if (!glfwInit()) return;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(1280, 800, "TestFlow Editor", nullptr, nullptr);
    if (!window) { glfwTerminate(); return; }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;

    // 日本語フォント
#ifdef TESTFLOW_FONT_PATH
    io.Fonts->AddFontFromFileTTF(TESTFLOW_FONT_PATH, 16.0f, nullptr,
                                  io.Fonts->GetGlyphRangesJapanese());
#endif

    ImGui::StyleColorsDark();
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // Dockspace
        ImGui::DockSpaceOverViewport(ImGui::GetMainViewport());

        // Main window with menu bar
        ImGuiWindowFlags main_flags =
            ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoDocking |
            ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse |
            ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
            ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus;
        ImGui::Begin("##main", nullptr, main_flags);
        render_menu_bar();
        ImGui::End();

        render_graph_view();
        render_property_panel();
        render_validation_panel();

        // Title bar dirty indicator
        std::string title = "TestFlow Editor";
        if (!doc_.file_path.empty()) title += " — " + doc_.file_path;
        if (doc_.dirty) title += " *";
        glfwSetWindowTitle(window, title.c_str());

        ImGui::Render();
        int w, h;
        glfwGetFramebufferSize(window, &w, &h);
        glViewport(0, 0, w, h);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        glfwSwapBuffers(window);
    }

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();
}

}  // namespace testflow
