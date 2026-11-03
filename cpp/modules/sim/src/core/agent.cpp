#include "cv/sim/core/agent.hpp"
#include "cv/sim/tasks.hpp"


Agent::Agent(std::string name, int agentId, Task* task) 
    : name_(name), agentId_(agentId), task_(task) {
    agentInfo_.name = name_;
    agentInfo_.detection.trackId = agentId_;
}


Detection Agent::run() {
    task_->calculate(agentInfo_);
    return agentInfo_.detection;
}