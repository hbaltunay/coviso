#pragma once

#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "cv/tool/logger.hpp"
#include "cv/core/types.hpp"

namespace cv {
class Mat;
}

struct Info {
    int infoId;
};

class State {
protected:
    Size<int> imgsz_; 
public:
    State(Size<int> imgsz);

    virtual std::vector<std::string> summary() = 0; 
    // virtual bool update() = 0;
    virtual bool add(int infoId, std::vector<Point2i> poly) = 0;
    virtual bool remove(int infoId) = 0;
    virtual void draw(cv::Mat& image) = 0;
};

// =============================================================================
// Zone State
// =============================================================================

struct ZoneInfo {
    int infoId = 0;
    int num = 0;
    std::vector<int> inZone;
    bool empty = true;
};

class ZoneState : public State {
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;

    int zoneNum_ = 0;

public:
    ZoneState(Size<int> imgsz);
    ~ZoneState();

    std::unordered_map<int, ZoneInfo> zoneInfos_;

    std::vector<std::string> summary() override;        
    bool add(int infoId, std::vector<Point2i> poly) override;
    bool remove(int infoId) override;

    bool updatePlain(std::unordered_map<int, int> zoneFreq);
    bool updateTracked();

    void draw(cv::Mat& image) override;
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
    int infoId = 0;
    int count = 0;
    int lineNum = 0;
    std::string lineType;
};

class LineState : public State {
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;

    int lineNum_ = 0;

public:
    LineState(Size<int> imgsz);
    ~LineState();

    std::unordered_map<int, LineInfo> lineInfos_;
    std::unordered_map<int, TrackInfo> trackInfos;

    std::vector<std::string> summary() override;        
    bool add(int infoId, std::vector<Point2i> poly) override;
    bool remove(int infoId) override;
    
    bool update();
    
    void draw(cv::Mat& image) override;
};