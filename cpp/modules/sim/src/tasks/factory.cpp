#include "cv/sim/tasks.hpp"


TaskFactory::TaskFactory() {
    tasks["Zone"] = []() { return std::make_unique<ZoneTask>(); };
    tasks["Line"] = []() { return std::make_unique<LineTask>(); };
}

std::unique_ptr<Task> TaskFactory::createTask(const std::string& taskName) {
    auto it = tasks.find(taskName);
    if (it != tasks.end()) {
        return it->second();
    }
    return nullptr;
}