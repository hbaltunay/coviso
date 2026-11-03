#pragma once

#include <vector>

#include "cv/core/types.hpp"
#include "cv/detect/core.hpp"
#include "cv/tool/config.hpp"
#include "cv/tool/logger.hpp"

namespace cv {
class Mat;
}

class BaseSolution {
protected:
    std::unique_ptr<Config> config_;
    std::filesystem::path configPath_;
    Size<int> imgsz_;
    std::string name_;


public:
    BaseSolution(std::filesystem::path configPath_);
    virtual void process(cv::Mat& image, std::vector<Detection> detection) = 0;
};