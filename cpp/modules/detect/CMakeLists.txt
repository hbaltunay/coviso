file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/*.cpp")

add_library(cv_detect ${SOURCES})

target_include_directories(cv_detect PUBLIC include)

target_link_libraries(cv_detect PRIVATE ${OpenCV_LIBS})