file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/*.cpp")

add_library(cv_core ${SOURCES})

target_include_directories(cv_core PUBLIC include)

target_link_libraries(cv_core PRIVATE ${OpenCV_LIBS})