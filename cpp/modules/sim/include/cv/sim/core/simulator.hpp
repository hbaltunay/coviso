#pragma once
#include <string>
#include <vector>

#include "cv/core/types.hpp"
#include "cv/sim/tasks.hpp"
#include "cv/sim/export.h"

namespace cv {
class Mat;
}

struct TaskList {
    std::string name;
    std::unique_ptr<Task> task;
};

class CVS_SIM_EXPORT Simulator {
private:
    Size<int> imgsz_;
    
    struct Impl;
    std::unique_ptr<Impl> impl_;

public:
    std::vector<TaskList> tasks_;

    Simulator(Size<int> imgsz);
    ~Simulator();

    bool addTask(std::string name, std::string taskName, int agentNum, int seed, int fps, Size<int> imgsz, CoordinateData coorData);
    bool addTaskConfig(std::string name, std::filesystem::path configPath);

    void run();
    void draw(cv::Mat& image, std::vector<Detection> detections);
    void writeState(cv::Mat& image, std::vector<std::string> strSummary);

    cv::Mat& getCanvas();
};