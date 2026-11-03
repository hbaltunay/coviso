#pragma once

#include "cv/sim/core/rng.hpp"
#include "cv/tool/logger.hpp"
#include "base.hpp"
#include "physics.hpp"

namespace cv {
class Mat;
}

struct ZonesData {
    const std::string name;
    const std::vector<std::vector<Point2i>> zone;

    ZonesData(std::string zoneName, std::vector<std::vector<Point2i>> zonePoints)
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
    Size<int> imgsz_;
    CoordinateData zones_;
    std::vector<ZonesData> zonesList_;
    int zoneNum_ = 0;

    struct Impl;
    std::unique_ptr<Impl> impl_;

    std::unordered_map<int, std::vector<Point2f>> coordinateMask;
    std::unordered_map<int, int> zoneInfo_;

public:
    ZoneTask();
    ~ZoneTask();

    bool init(TaskData taskData) override;
    std::vector<Detection> generate() override;
    void calculate(AgentInfo& agentInfo) override;

    bool createMask();

    int getZoneValue(Point2f coord);
    void assignRandomTarget(const std::shared_ptr<AgentZData>& agentData);

    cv::Mat getMask();

    void drawCanvas(cv::Mat& canvas) override;
    void drawCanvasStatus(cv::Mat& canvas) override;

    int getPolyNum() { return zoneNum_; }
};
