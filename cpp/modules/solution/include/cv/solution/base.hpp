#pragma once

#include <vector>
#include <opencv2/opencv.hpp>

#include "cv/detect/core.hpp"
#include "cv/tool/config.hpp"


using Coordinate2D = std::vector<int>;
using CoordinateList = std::vector<Coordinate2D>;
using InnerMap = std::map<std::string, CoordinateList>;
using CoordinateData = std::map<std::string, InnerMap>;


class BaseSolution {
protected:
    std::string name_;
    std::filesystem::path configPath_;

public:
    BaseSolution(std::filesystem::path configPath_);
    virtual void process(cv::Mat& image, std::vector<Detection> detection) = 0;
};