#pragma once

#include <vector>
#include <string>
#include <utility>
#include <unordered_map>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include "cv/tool/logger.hpp"


struct Info {
    int infoId;
};

class State {
protected:
    cv::Size imgsz_; 
public:
    State(cv::Size imgsz);

    virtual std::vector<std::string> summary() = 0; 
    // virtual bool update() = 0;
    virtual bool add(int infoId, std::vector<cv::Point> poly) = 0;
    virtual bool remove(int infoId) = 0;
};

// =============================================================================
// Zone State
// =============================================================================

struct ZoneInfo {
    int infoId = 0;
    int num = 0;
    std::vector<cv::Point> zone;
    std::vector<int> inZone;
    bool empty = true;

    cv::Mat mask;

    cv::Rect roi;
    cv::Mat maskRoiU8;
    cv::Mat oneRoi;
    cv::Mat zeroRoi;
    cv::Mat blended;
    bool ready = false;

    ZoneInfo() = default;

    ZoneInfo(int infoId_, int num_, std::vector<cv::Point> zone_,
         std::vector<int> inZone_ = {}, bool empty_ = true, cv::Mat mask_ = cv::Mat())
        : infoId(infoId_), num(num_), zone(std::move(zone_)),
        inZone(std::move(inZone_)), empty(empty_), mask(std::move(mask_)) {
        postInit();
    }

    void postInit() {
        ready = false;
        if (mask.empty()) return;

        roi = cv::boundingRect(mask);
        if (roi.area() == 0) return;

        maskRoiU8 = (mask(roi) != 0);

        oneRoi  = cv::Mat(roi.size(), CV_8UC3, cv::Scalar(0, 0, 255));
        zeroRoi = cv::Mat(roi.size(), CV_8UC3, cv::Scalar(0, 255, 0));
        blended = cv::Mat(roi.size(), CV_8UC3);

        ready = true;
    }
};


class ZoneState : public State {
public:
    ZoneState(cv::Size imgsz);

    std::unordered_map<int, ZoneInfo> zoneInfos_;

    std::vector<std::string> summary() override;        
    bool add(int infoId, std::vector<cv::Point> poly) override;
    bool remove(int infoId) override;

    bool updatePlain(std::unordered_map<int, int> zoneFreq);
    bool updateTracked();

    std::unordered_map<int, ZoneInfo> infos() { return zoneInfos_; }
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
    std::vector<cv::Point> line;

    cv::Mat mask;

    cv::Rect roi;
    cv::Mat maskRoiU8;
    cv::Mat lineRoi;
    cv::Mat blended;
    bool ready = false;

    LineInfo() = default;

    LineInfo(int infoId_, int count_, int lineNum_, std::string lineType_,
             std::vector<cv::Point> line_, cv::Mat mask_ = cv::Mat())
        : infoId(infoId_), count(count_), lineNum(lineNum_),
          lineType(std::move(lineType_)), line(std::move(line_)),
          mask(std::move(mask_)) {
        postInit();
    }

    void postInit() {
        ready = false;
        if (mask.empty()) return;

        roi = cv::boundingRect(mask);
        if (roi.area() == 0) return;

        maskRoiU8 = (mask(roi) != 0);

        const cv::Scalar color = (lineType == "entry")
                                     ? cv::Scalar(0, 255, 0)
                                     : cv::Scalar(0, 0, 255);
        lineRoi = cv::Mat(roi.size(), CV_8UC3, color);
        blended = cv::Mat(roi.size(), CV_8UC3);

        ready = true;
    }
};

class LineState : public State {
public:
    LineState(cv::Size imgsz);

    std::unordered_map<int, LineInfo> lineInfos_;
    std::unordered_map<int, TrackInfo> trackInfos;

    std::vector<std::string> summary() override;        
    bool add(int infoId, std::vector<cv::Point> poly) override;
    bool remove(int infoId) override;

    bool update();

    std::unordered_map<int, LineInfo> infos() { return lineInfos_; }
};