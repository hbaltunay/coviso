#pragma once

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include "cv/sim/core/agent.hpp"
#include "cv/tool/config.hpp"


using Coordinate2D = std::vector<int>;
using CoordinateList = std::vector<Coordinate2D>;
using InnerMap = std::map<std::string, CoordinateList>;
using CoordinateData = std::map<std::string, InnerMap>;

struct TaskData {
    int agentNum;
    int seed;
    int fps;
    cv::Size imgsz; 
    CoordinateData coorData;
};

struct AgentData {
    virtual ~AgentData() = default;
};

class Task {
private:
    std::vector<std::unique_ptr<Agent>> agents_;
    std::unordered_map<std::string, std::shared_ptr<AgentData>> agentData_;

public:
    int seed_;

    virtual bool init(TaskData taskData) = 0;
    virtual std::vector<Detection> generate() = 0;
    virtual void calculate(AgentInfo& agentInfo) = 0;


    void addAgent(std::unique_ptr<Agent> agent) {
        agents_.push_back(std::move(agent));
        
    }

    const std::vector<std::unique_ptr<Agent>>& getAgents() const { 
        return agents_; 
    }

    virtual void drawCanvas(cv::Mat& canvas) = 0;
    virtual void drawCanvasStatus(cv::Mat& canvas) = 0;

    template <typename T>
    void addAgentData(const std::string& name, std::shared_ptr<T> data) {
        agentData_[name] = data; 
    }

    template <typename T>
    std::shared_ptr<T> getAgentData(const std::string& name) {
        auto it = agentData_.find(name);
        if (it != agentData_.end()) {
            return std::static_pointer_cast<T>(it->second);
        }
        return nullptr;
    }

    std::unordered_map<std::string, std::shared_ptr<AgentData>>& getAgentMap() {
        return agentData_;
    }

    virtual int getPolyNum() = 0;
};