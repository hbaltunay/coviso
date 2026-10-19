#include <iostream>
#include "cv/sim/core.hpp"


Simulator::Simulator(cv::Size imgsz) : imgsz_(imgsz) {
    canvas_ = cv::Mat::zeros(imgsz_, CV_8UC1);
}


bool Simulator::addTask(std::string name, std::string taskName, int agentNum, int seed, int fps, cv::Size imgsz, CoordinateData coorData) {
    std::unique_ptr<Task> task = TaskFactory::getInstance().createTask(taskName);

    TaskData taskData{agentNum, seed, fps, imgsz, coorData};

    bool success = task->init(taskData);
    if (!success) return false;

    task->drawCanvas(canvas_);

    tasks_.push_back({name, std::move(task)});

    return true;
}

bool Simulator::addTaskConfig(std::string name, std::filesystem::path configPath) {
    Config config(configPath);
    if (!config.load()) return false;

    std::string taskName = config.get_or<std::string>("taskName", "");
    if (taskName.empty()) return false;

    cv::Size imgsz = config.get_or<cv::Size>("imgsz", cv::Size());
    if (imgsz.width <= 0 || imgsz.height <= 0) return false;

    CoordinateData coorData = config.get_or<CoordinateData>("points", {});
    if (coorData.empty()) return false;

    int agentNum = config.get_or<int>("agentNum", 1);
    int seed = config.get_or<int>("seed", 123);
    int fps = config.get_or<int>("fps", 30);

    bool success = addTask(name, taskName, agentNum, seed, fps, imgsz, coorData);

    return success;
}

void Simulator::run() {
    while (true) {

        cv::Mat display_canvas;
        canvas_.copyTo(display_canvas);

        for (const auto& [name, task]: tasks_) {
            std::vector<Detection> detectionList = task->generate();

            draw(display_canvas, detectionList, task->getPolyNum());

            task->drawCanvasStatus(display_canvas);
        }

        cv::imshow("Simulation", display_canvas);

        if (cv::waitKey(10) == 27) break; 
    }
}

void Simulator::draw(cv::Mat& image, std::vector<Detection> detections, int color) {
    for (Detection detection : detections) {
        cv::Point center(detection.bbox.x, detection.bbox.y);
        cv::circle(image, center, 5, cv::Scalar(color + 1), -1);
    }

    cv::normalize(image, image, 0, 255, cv::NORM_MINMAX);
}

void Simulator::writeState(cv::Mat& image, std::vector<std::string> strSummary) {
    int startX = 15;
    int startY = 30;
    int lineSpacing = 25;

    for (std::string text : strSummary) {
        cv::putText(image, 
                    text, 
                    cv::Point(startX, startY), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    0.9,
                    cv::Scalar(255),
                    1,
                    cv::LINE_AA);
        startY += lineSpacing;
    }
}