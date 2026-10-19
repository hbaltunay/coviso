#pragma once

#include <unordered_map>
#include <string>
#include <memory>
#include <functional>

#include "cv/sim/tasks.hpp"


class TaskFactory {
private:
    std::unordered_map<std::string, std::function<std::unique_ptr<Task>()>> tasks;

    TaskFactory();

public:
    TaskFactory(const TaskFactory&) = delete;
    TaskFactory& operator=(const TaskFactory&) = delete;

    static TaskFactory& getInstance() {
        static TaskFactory instance;
        return instance;
    }

    std::unique_ptr<Task> createTask(const std::string& taskName);
};