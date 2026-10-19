#pragma once

#include <iostream>
#include <memory>

#include "cv/detect/core.hpp"

struct AgentInfo {
    std::string name;
    Detection detection;
};

class Task;

class Agent {
private:
    std::string name_;
    int id_;
    AgentInfo agentInfo_;
    Task* task_;

    
public:
    Agent(std::string name, int id, Task* task);

    Detection run();
};