#include "cv/solution/state.hpp"

// =============================================================================
// State
// =============================================================================

State::State(cv::Size imgsz) : imgsz_(imgsz) {}

// =============================================================================
// Zone State
// =============================================================================

ZoneState::ZoneState(cv::Size imgsz) : State(imgsz) {}

std::vector<std::string> ZoneState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 0; i < zoneInfos_.size(); i++) {
        ZoneInfo& zoneInfo = zoneInfos_[i];
        std::string strInfo = "[ Zone-" + std::to_string(zoneInfo.infoId) + " ] : " + std::to_string(zoneInfo.num); 
        strInfos.push_back(strInfo);
    }

    return strInfos;
}

bool ZoneState::add(int infoId, std::vector<cv::Point> poly) {
    cv::Mat mask;
    
    if (infoId > 0) {
        mask = cv::Mat::zeros(imgsz_, CV_8UC1);

        std::vector<std::vector<cv::Point>> polys{poly};
        cv::fillPoly(mask, polys, cv::Scalar(255));
    }
    
    zoneInfos_.insert_or_assign(infoId, ZoneInfo(infoId, 0, poly, {}, false, mask));

    return true;
}

bool ZoneState::remove(int infoId) {
    return true; // TODO
}

bool ZoneState::updatePlain(std::unordered_map<int, int> zoneFreq) {
    for (int i = 0; i < zoneInfos_.size(); i++) {
        zoneInfos_[i].num = zoneFreq[i];
        zoneInfos_[i].empty = zoneInfos_[i].num == 0;
    }
    return true;
}

bool ZoneState::updateTracked() {
    for (int i = 0; i < zoneInfos_.size(); i++) {
        zoneInfos_[i].num = zoneInfos_[i].inZone.size();
        zoneInfos_[i].empty = zoneInfos_[i].num == 0;
        zoneInfos_[i].inZone.clear();
    }
    return true;
}

// =============================================================================
// Line State
// =============================================================================

LineState::LineState(cv::Size imgsz) : State(imgsz) {}

std::vector<std::string> LineState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 1; i <= lineInfos_.size(); i++) {
        LineInfo& lineInfo = lineInfos_[i];
        std::string strInfo = "[ Line-" + std::to_string(lineInfo.infoId) + "-" + lineInfo.lineType + " ] : " +  std::to_string(lineInfo.count);
        strInfos.push_back(strInfo);
    }
    return strInfos;
}

bool LineState::add(int infoId, std::vector<cv::Point> poly) {
    const bool isEntry = (infoId % 2 == 1);
    const std::string lineType = isEntry ? "entry" : "exit";
    const int lineNum = isEntry ? infoId + 1 : infoId - 1;

    cv::Mat mask = cv::Mat::zeros(imgsz_, CV_8UC1);

    std::vector<std::vector<cv::Point>> polys{poly};
    cv::fillPoly(mask, polys, cv::Scalar(255));

    lineInfos_.insert_or_assign(
        infoId, LineInfo(infoId, 0, lineNum, lineType, poly, mask));
    return true;
}

bool LineState::remove(int infoId) {
    return true; // TODO
}

bool LineState::update() {
    return true;
}