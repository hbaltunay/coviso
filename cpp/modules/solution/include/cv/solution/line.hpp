#pragma once

#include <vector>

#include "base.hpp"
#include "state.hpp"
#include "cv/tool/logger.hpp"
#include "cv/solution/export.h"


class CVS_SOLUTION_EXPORT LineTracker : public BaseSolution {
private:
    LineState state_;
    
    struct Impl;
    std::unique_ptr<Impl> impl_;

    CoordinateData lines_;
    int lineNum_ = 0;

public:
    LineTracker(std::filesystem::path configPath);
    ~LineTracker();


    bool init();
    std::vector<std::vector<cv::Point>> createLineZones(cv::Point firstPoint, cv::Point secondPoint, float width, float angle);
    bool createMask();
    void process(cv::Mat& image, std::vector<Detection> detections) override;
    void draw(cv::Mat& image);
    std::vector<std::string> getStateInfoStr();
    int getLineNum() { return lineNum_; }
};