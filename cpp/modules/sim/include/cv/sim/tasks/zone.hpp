#pragma once

#include <unordered_map>

#include "base.hpp"
#include "physics.hpp"
#include "cv/sim/core/rng.hpp"
#include "cv/tool/logger.hpp"


struct ZonesData {
    const std::string name;
    const std::vector<std::vector<cv::Point>> zone;

    ZonesData(std::string zoneName, std::vector<std::vector<cv::Point>> zonePoints)
        : name(std::move(zoneName)), zone(std::move(zonePoints)) {}
};

struct AgentZData : public AgentData {
    Rng rng{0, 0};
    MoveData moveData;
    int targetZone;
    int currentZone;
};


class ZoneTask : public Task {
private:
    int agentNum_;
    int fps_;
    cv::Size imgsz_;
    CoordinateData zones_;
    std::vector<ZonesData> zonesList_;
    int zoneNum_;

    cv::Mat mask_;
    std::unordered_map<int, std::vector<cv::Point>> coordinateMask;
    std::unordered_map<int, int> zoneInfo_;

public:
    bool init(TaskData taskData) override;
    std::vector<Detection> generate() override;
    void calculate(AgentInfo& agentInfo) override;

    bool createMask();

    int getZoneValue(cv::Point2f coord);
    void assignRandomTarget(const std::shared_ptr<AgentZData>& agentData);

    cv::Mat getMask() { return mask_; }

    void drawCanvas(cv::Mat& canvas) override;
    void drawCanvasStatus(cv::Mat& canvas) override;

    int getPolyNum() { return zoneNum_; }
};
