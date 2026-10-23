#pragma once

#include <vector>

#include "base.hpp"
#include "state.hpp"
#include "cv/tool/logger.hpp"


class LineTracker : public BaseSolution {
private:
    cv::Mat mask_;
    CoordinateData lines_;
    int lineNum_;

public:
    LineTracker(std::filesystem::path configPath);
    ~LineTracker();

    LineState state_;

    bool init();
    std::vector<std::vector<cv::Point>> createLineZones(cv::Point firstPoint, cv::Point secondPoint, float width, float angle);
    bool createMask();
    void process(cv::Mat& image, std::vector<Detection> detections) override;
    void draw(cv::Mat& image);
    std::vector<std::string> getStateInfoStr();
    int getLineNum() { return lineNum_; }
};