cmake_minimum_required(VERSION 3.20)
project(testflow_editor VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --------------------------------------------------------------------------
# Dependencies via FetchContent
# --------------------------------------------------------------------------
include(FetchContent)

# Dear ImGui
FetchContent_Declare(
    imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui.git
    GIT_TAG        v1.91.6
    GIT_SHALLOW    TRUE
)

# imgui-node-editor
FetchContent_Declare(
    imgui_node_editor
    GIT_REPOSITORY https://github.com/thedmd/imgui-node-editor.git
    GIT_TAG        v0.9.3
    GIT_SHALLOW    TRUE
)

# nlohmann/json
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
    GIT_SHALLOW    TRUE
)

FetchContent_MakeAvailable(imgui imgui_node_editor nlohmann_json)

# --------------------------------------------------------------------------
# Find GLFW
# --------------------------------------------------------------------------
find_package(glfw3 REQUIRED)
find_package(OpenGL REQUIRED)

# --------------------------------------------------------------------------
# ImGui library
# --------------------------------------------------------------------------
add_library(imgui_lib STATIC
    ${imgui_SOURCE_DIR}/imgui.cpp
    ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_glfw.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp
)
target_include_directories(imgui_lib PUBLIC
    ${imgui_SOURCE_DIR}
    ${imgui_SOURCE_DIR}/backends
)
target_link_libraries(imgui_lib PUBLIC glfw OpenGL::GL)

# --------------------------------------------------------------------------
# imgui-node-editor library
# --------------------------------------------------------------------------
file(GLOB NODE_EDITOR_SOURCES ${imgui_node_editor_SOURCE_DIR}/*.cpp)
add_library(imgui_node_editor_lib STATIC ${NODE_EDITOR_SOURCES})
target_include_directories(imgui_node_editor_lib PUBLIC ${imgui_node_editor_SOURCE_DIR})
target_link_libraries(imgui_node_editor_lib PUBLIC imgui_lib)

# --------------------------------------------------------------------------
# Main executable
# --------------------------------------------------------------------------
add_executable(testflow_editor
    src/main.cpp
    src/app.cpp
    src/dsl_loader.cpp
    src/dsl_saver.cpp
    src/graph_view.cpp
    src/property_panel.cpp
    src/validator_runner.cpp
)

target_include_directories(testflow_editor PRIVATE src)
target_link_libraries(testflow_editor PRIVATE
    imgui_lib
    imgui_node_editor_lib
    nlohmann_json::nlohmann_json
)

# --------------------------------------------------------------------------
# Platform: Linux font path for Japanese
# --------------------------------------------------------------------------
if(UNIX AND NOT APPLE)
    target_compile_definitions(testflow_editor PRIVATE
        TESTFLOW_FONT_PATH="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    )
endif()

if(WIN32)
    target_compile_definitions(testflow_editor PRIVATE
        TESTFLOW_FONT_PATH="C:/Windows/Fonts/msgothic.ttc"
    )
endif()
