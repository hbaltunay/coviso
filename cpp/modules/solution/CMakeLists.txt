file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/*.cpp")

add_library(cv_solution ${SOURCES})

target_include_directories(cv_solution PUBLIC include)

target_link_libraries(cv_solution PRIVATE ${OpenCV_LIBS} cv_core cv_detect cv_tool)