add_executable(app main.cpp)

target_link_libraries(app PRIVATE 
    cv_core
    cv_detect
    cv_sim
    cv_solution
    cv_tool
)