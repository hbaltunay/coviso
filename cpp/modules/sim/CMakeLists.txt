file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/core/*.cpp" "src/tasks/*.cpp")

add_library(cv_sim ${SOURCES})

target_include_directories(cv_sim PUBLIC include)

target_link_libraries(cv_sim PRIVATE 
    ${OpenCV_LIBS} 
    spdlog::spdlog 
    nlohmann_json::nlohmann_json
    cv_detect
    cv_tool
)