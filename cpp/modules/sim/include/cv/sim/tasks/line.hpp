#pragma once

#include "base.hpp"
#include "physics.hpp"
#include "cv/sim/core/rng.hpp"
#include "cv/tool/logger.hpp"


struct LineInfoData {
    const std::string name;
    const cv::Point firstPoint;
    const cv::Point secondPoint;
    const float width;
    const float angle;
    const std::vector<std::vector<cv::Point>> entryZone;
    const std::vector<std::vector<cv::Point>> exitZone;

    LineInfoData(std::string lineName, cv::Point lineFirstPoint, cv::Point lineSecondPoint,
        float lineWidth, float lineAngle, std::vector<std::vector<cv::Point>> lineEntryZone,
        std::vector<std::vector<cv::Point>> lineExitZone) : name(std::move(lineName)), 
        firstPoint(std::move(lineFirstPoint)), secondPoint(std::move(lineSecondPoint)),
        width(std::move(lineWidth)), angle(std::move(lineAngle)), entryZone(std::move(lineEntryZone)),
        exitZone(std::move(lineExitZone)) {}
};

struct LineData {
    const std::string name;
    const std::vector<std::vector<cv::Point>> line;

    LineData(std::string lineName, std::vector<std::vector<cv::Point>> linePoints)
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
    cv::Size imgsz_;
    CoordinateData lines_;
    std::vector<LineInfoData> linesInfoList_;
    std::vector<LineData> linesList_;
    int lineNum_;

    cv::Mat mask_;
    std::unordered_map<int, std::vector<cv::Point>> coordinateMask;
    std::unordered_map<int, LinePassedInfo> lineInfo_;

public:
    bool init(TaskData taskData) override;
    std::vector<Detection> generate() override;
    void calculate(AgentInfo& agentInfo) override;

    std::vector<std::vector<cv::Point>> createLineZones(cv::Point firstPoint, cv::Point secondPoint, float width, float angle);
    bool createMask();

    int getLineValue(cv::Point2f coord);
    void assignRandomTarget(const std::shared_ptr<AgentLData>& agentData);
    

    cv::Mat getMask() { return mask_; }

    void drawCanvas(cv::Mat& canvas) override;
    void drawCanvasStatus(cv::Mat& canvas) override;

    int getPolyNum() { return lineNum_; }
};