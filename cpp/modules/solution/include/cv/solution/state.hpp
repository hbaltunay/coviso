#pragma once

#include <vector>
#include <string>
#include <utility>
#include <unordered_map>
#include <opencv2/core.hpp>

struct Info {
    int id;
};

class State {
public:
    virtual std::vector<std::string> summary() = 0; 
    // virtual bool update() = 0;
    virtual bool add(int id, std::vector<cv::Point> zone) = 0;
    virtual bool remove(int id) = 0;
};

// =============================================================================
// Zone State
// =============================================================================

struct ZoneInfo {
    int id;
    int num;
    std::vector<cv::Point> zone;
    std::vector<int> inZone;
};


class ZoneState : public State {
public:
    std::unordered_map<int, ZoneInfo> zoneInfos_;

    std::vector<std::string> summary() override;        
    bool add(int id, std::vector<cv::Point> zone) override;
    bool remove(int id) override;

    bool updatePlain(std::unordered_map<int, int> zoneFreq);
    bool updateTracked();
};

// =============================================================================
// Line State
// =============================================================================

struct TrackInfo {
    int currentLine = 0;
    int lastLine = 0;
    bool passed = false;
    int passedNum = 0;
};

struct LineInfo {
    int id;
    int count;
    int lineNum;
    std::string lineType;
    std::vector<cv::Point> line;
};

class LineState : public State {
public:
    std::unordered_map<int, LineInfo> lineInfos_;
    std::unordered_map<int, TrackInfo> trackInfos;

    std::vector<std::string> summary() override;        
    bool add(int id, std::vector<cv::Point> line) override;
    bool remove(int id) override;

    bool update();
};