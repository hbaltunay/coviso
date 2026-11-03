#pragma once

#include <vector>

#include "base.hpp"
#include "state.hpp"
#include "cv/tool/logger.hpp"
#include "cv/tool/export.h"



class CVS_EXPORT ZoneTracker : public BaseSolution {
private:
    std::string strategy_;

    ZoneState state_;

    struct Impl;
    std::unique_ptr<Impl> impl_;
    
    CoordinateData zones_;
    int zoneNum_ = 0;

    void (ZoneTracker::*activeStrategy)(std::vector<Detection> detections);
    void trackedStrategy(std::vector<Detection> detections);
    void plainStrategy(std::vector<Detection> detections);

public:
    ZoneTracker(std::filesystem::path configPath, std::string strategy = "plain");
    ~ZoneTracker();

    bool init();
    bool createMask();
    void process(cv::Mat& image, std::vector<Detection> detections) override;
    void draw(cv::Mat& image);
    std::vector<std::string> getStateInfoStr();
    int getZoneNum() { return zoneNum_; }
};