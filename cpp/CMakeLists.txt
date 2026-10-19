list(APPEND CMAKE_PREFIX_PATH
    "/opt/spdlog"
    "/opt/nlohmann_json"
)

find_package(nlohmann_json REQUIRED)
find_package(spdlog REQUIRED)
find_package(OpenCV REQUIRED)

#find_package(pybind11 REQUIRED)

add_subdirectory(modules/core)
add_subdirectory(modules/detect)
add_subdirectory(modules/sim)
add_subdirectory(modules/solution)
add_subdirectory(modules/tool)

add_subdirectory(apps)