#pragma once

#include "base.hpp"
#include "physics.hpp"
#include "cv/sim/core/rng.hpp"
#include "cv/tool/logger.hpp"


struct LineInfoData {
    const std::string name;
    const Point2i firstPoint;
    const Point2i secondPoint;
    const float width;
    const float angle;
    const std::vector<std::vector<Point2i>> entryZone;
    const std::vector<std::vector<Point2i>> exitZone;

    LineInfoData(std::string lineName, Point2i lineFirstPoint, Point2i lineSecondPoint,
        float lineWidth, float lineAngle, std::vector<std::vector<Point2i>> lineEntryZone,
        std::vector<std::vector<Point2i>> lineExitZone) : name(std::move(lineName)), 
        firstPoint(std::move(lineFirstPoint)), secondPoint(std::move(lineSecondPoint)),
        width(std::move(lineWidth)), angle(std::move(lineAngle)), entryZone(std::move(lineEntryZone)),
        exitZone(std::move(lineExitZone)) {}
};

struct LineData {
    const std::string name;
    const std::vector<std::vector<Point2i>> line;

    LineData(std::string lineName, std::vector<std::vector<Point2i>> linePoints)
        : name(std::move(lineName)), line(std::move(linePoints)) {}
};

struct LinePassedInfo {
    std::string lineName;
    std::string lineType;
    int lineNum;
    int count;
};

struct AgentLData : public AgentData {
    Rng rng{0, 0};
    MoveData moveData;
    int targetLine;
    int currentLine;
    int lastLine;
    bool passed;
    int passedNum;
};

class LineTask : public Task {
private:
    int agentNum_;
    int fps_;
    Size<int> imgsz_;
    CoordinateData lines_;
    std::vector<LineInfoData> linesInfoList_;
    std::vector<LineData> linesList_;
    int lineNum_ = 0;

    struct Impl;
    std::unique_ptr<Impl> impl_;

    std::unordered_map<int, std::vector<Point2f>> coordinateMask;
    std::unordered_map<int, LinePassedInfo> lineInfo_;

public:
    LineTask();
    ~LineTask();

    bool init(TaskData taskData) override;
    std::vector<Detection> generate() override;
    void calculate(AgentInfo& agentInfo) override;

    std::vector<std::vector<Point2i>> createLineZones(Point2i firstPoint, Point2i secondPoint, float width, float angle);
    bool createMask();

    int getLineValue(Point2f coord);
    void assignRandomTarget(const std::shared_ptr<AgentLData>& agentData);
    

    cv::Mat getMask();

    void drawCanvas(cv::Mat& canvas) override;
    void drawCanvasStatus(cv::Mat& canvas) override;

    int getPolyNum() { return lineNum_; }
};