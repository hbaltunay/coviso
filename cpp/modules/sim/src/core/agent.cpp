#include "cv/sim/core/agent.hpp"
#include "cv/sim/tasks.hpp"


Agent::Agent(std::string name, int id, Task* task) 
    : name_(name), id_(id), task_(task) {
    agentInfo_.name = name_;
    agentInfo_.detection.id = id_;
}


Detection Agent::run() {
    task_->calculate(agentInfo_);
    return agentInfo_.detection;
}