file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/*.cpp")

add_library(cv_tool ${SOURCES})

target_include_directories(cv_tool PUBLIC include ${OpenCV_INCLUDE_DIRS})

target_link_libraries(cv_tool PRIVATE ${OpenCV_LIBS} cv_solution cv_detect)