add_executable(app main.cpp)

find_package(OpenCV REQUIRED)

target_link_libraries(app PRIVATE 
    ${OpenCV_LIBS} 
    cv_sim
    cv_solution
    cv_tool
)