#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include "cv/solution/state.hpp"
#include "utils.hpp"

// =============================================================================
// State
// =============================================================================

State::State(Size<int> imgsz) : imgsz_(imgsz) {}

// =============================================================================
// Zone State
// =============================================================================

struct ZoneDrawInfo {
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

    ZoneDrawInfo() = default;

    ZoneDrawInfo(int infoId_, int num_, std::vector<cv::Point> zone_,
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

struct ZoneState::Impl {
    std::unordered_map<int, ZoneDrawInfo> zoneDrawInfos;
};

ZoneState::ZoneState(Size<int> imgsz) : State(imgsz), impl_(std::make_unique<Impl>()) {}

ZoneState::~ZoneState() = default;

std::vector<std::string> ZoneState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 0; i < zoneNum_; i++) {
        ZoneInfo& zoneInfo = zoneInfos_[i];
        std::string strInfo = "[ Zone-" + std::to_string(zoneInfo.infoId) + " ] : " + std::to_string(zoneInfo.num); 
        strInfos.push_back(strInfo);
    }

    return strInfos;
}

bool ZoneState::add(int infoId, std::vector<Point2i> poly) {
    cv::Mat mask;
    std::vector<cv::Point> polyCv = toCv(poly);
    
    if (infoId > 0) {
        mask = cv::Mat::zeros(imgsz_.height, imgsz_.width, CV_8UC1);
        cv::fillPoly(mask, {polyCv}, cv::Scalar(255));
    }
    
    impl_->zoneDrawInfos.insert_or_assign(infoId, ZoneDrawInfo(infoId, 0, polyCv, {}, false, mask));
    zoneInfos_.insert_or_assign(infoId, ZoneInfo{infoId, 0, {}, false});

    zoneNum_++;

    return true;
}

bool ZoneState::remove(int infoId) {
    impl_->zoneDrawInfos.erase(infoId);
    return zoneInfos_.erase(infoId) > 0;
}

bool ZoneState::updatePlain(std::unordered_map<int, int> zoneFreq) {
    for (int i = 0; i < zoneNum_; i++) {
        zoneInfos_[i].num = zoneFreq[i];
        zoneInfos_[i].empty = zoneInfos_[i].num == 0;
    }
    return true;
}

bool ZoneState::updateTracked() {
    for (int i = 0; i < zoneNum_; i++) {
        zoneInfos_[i].num = zoneInfos_[i].inZone.size();
        zoneInfos_[i].empty = zoneInfos_[i].num == 0;
        zoneInfos_[i].inZone.clear();
    }
    return true;
}

void ZoneState::draw(cv::Mat& image) {
    for (auto& [zoneId, zone] : impl_->zoneDrawInfos) {
        if (zoneId == 0 || !zone.ready) continue;

        cv::Mat roi = image(zone.roi);
        const cv::Mat& overlay = zoneInfos_[zoneId].empty ? zone.zeroRoi : zone.oneRoi;
        cv::addWeighted(roi, 0.4, overlay, 0.6, 0.0, zone.blended);
        zone.blended.copyTo(roi, zone.maskRoiU8);
    }
}

// =============================================================================
// Line State
// =============================================================================

struct LineDrawInfo {
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

    LineDrawInfo() = default;

    LineDrawInfo(int infoId_, int count_, int lineNum_, std::string lineType_,
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

struct LineState::Impl {
    std::unordered_map<int, LineDrawInfo> lineDrawInfos;
};

LineState::LineState(Size<int> imgsz) : State(imgsz), impl_(std::make_unique<Impl>()) {}

LineState::~LineState() = default;

std::vector<std::string> LineState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 1; i <= lineNum_; i++) {
        LineInfo& lineInfo = lineInfos_[i];
        std::string strInfo = "[ Line-" + std::to_string(lineInfo.infoId) + "-" + lineInfo.lineType + " ] : " +  std::to_string(lineInfo.count);
        strInfos.push_back(strInfo);
    }
    return strInfos;
}

bool LineState::add(int infoId, std::vector<Point2i> poly) {
    const bool isEntry = (infoId % 2 == 1);
    const std::string lineType = isEntry ? "entry" : "exit";
    const int lineNum = isEntry ? infoId + 1 : infoId - 1;

    cv::Mat mask = cv::Mat::zeros(imgsz_.height, imgsz_.width, CV_8UC1);

    std::vector<cv::Point> polyCv = toCv(poly);
    cv::fillPoly(mask, {polyCv}, cv::Scalar(255));

    impl_->lineDrawInfos.insert_or_assign(
        infoId, LineDrawInfo(infoId, 0, lineNum, lineType, polyCv, mask));
    lineInfos_.insert_or_assign(
        infoId, LineInfo{infoId, 0, lineNum, lineType});

    lineNum_++;

    return true;
}

bool LineState::remove(int infoId) {
    return lineInfos_.erase(infoId) > 0;
}

bool LineState::update() {
    return true;
}

void LineState::draw(cv::Mat& image) {
    for (auto& [lineId, line] : impl_->lineDrawInfos) {
        if (!line.ready) continue;

        cv::Mat roi = image(line.roi);
        cv::addWeighted(roi, 0.4, line.lineRoi, 0.6, 0.0, line.blended);
        line.blended.copyTo(roi, line.maskRoiU8);
    }
} 