#pragma once
#include <string>
#include <vector>
#include <opencv2/core.hpp>

#include "cv/sim/tasks.hpp"

struct TaskList {
    std::string name;
    std::unique_ptr<Task> task;
};

class Simulator {
private:
    cv::Size imgsz_;

public:
    cv::Mat canvas_;
    std::vector<TaskList> tasks_;

    Simulator(cv::Size imgsz);

    bool addTask(std::string name, std::string taskName, int agentNum, int seed, int fps, cv::Size imgsz, CoordinateData coorData);
    bool addTaskConfig(std::string name, std::filesystem::path configPath);

    void run();
    void draw(cv::Mat& image, std::vector<Detection> detections);
    void writeState(cv::Mat& image, std::vector<std::string> strSummary);

    cv::Mat& getCanvas() { return canvas_; }
};