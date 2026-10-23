#pragma once

#include <vector>

#include "base.hpp"
#include "state.hpp"
#include "cv/tool/logger.hpp"


class ZoneTracker : public BaseSolution {
private:
    std::string strategy_;
    cv::Mat mask_;
    CoordinateData zones_;
    int zoneNum_;

    void (ZoneTracker::*activeStrategy)(std::vector<Detection> detections);
    void trackedStrategy(std::vector<Detection> detections);
    void plainStrategy(std::vector<Detection> detections);

public:
    ZoneTracker(std::filesystem::path configPath, std::string strategy = "plain");
    ~ZoneTracker();

    ZoneState state_;

    bool init();
    bool createMask();
    void process(cv::Mat& image, std::vector<Detection> detections) override;
    void draw(cv::Mat& image);
    std::vector<std::string> getStateInfoStr();
    int getZoneNum() { return zoneNum_; }
};