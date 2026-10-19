#include "cv/solution/state.hpp"

// =============================================================================
// Zone State
// =============================================================================

std::vector<std::string> ZoneState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 0; i < zoneInfos_.size(); i++) {
        ZoneInfo& zoneInfo = zoneInfos_[i];
        std::string strInfo = "[ Zone-" + std::to_string(zoneInfo.id) + " ] : " + std::to_string(zoneInfo.num); 
        strInfos.push_back(strInfo);
    }

    return strInfos;
}

bool ZoneState::add(int id, std::vector<cv::Point> zone) {
    ZoneInfo zoneInfo{id, 0, zone};
    zoneInfos_.insert({id, zoneInfo});
    return true;
}

bool ZoneState::remove(int id) {
    return true; // TODO
}

bool ZoneState::updatePlain(std::unordered_map<int, int> zoneFreq) {
    for (int i = 0; i < zoneInfos_.size(); i++) {
        zoneInfos_[i].num = zoneFreq[i];
    }
    return true;
}

bool ZoneState::updateTracked() {
    for (int i = 0; i < zoneInfos_.size(); i++) {
        zoneInfos_[i].num = zoneInfos_[i].inZone.size();
        zoneInfos_[i].inZone.clear();
    }
    return true;
}

// =============================================================================
// Line State
// =============================================================================

std::vector<std::string> LineState::summary() {
    std::vector<std::string> strInfos;
    for (int i = 1; i <= lineInfos_.size(); i++) {
        LineInfo& lineInfo = lineInfos_[i];
        std::string strInfo = "[ Line-" + std::to_string(lineInfo.id) + "-" + lineInfo.lineType + " ] : " +  std::to_string(lineInfo.count);
        strInfos.push_back(strInfo);
    }
    return strInfos;
}

bool LineState::add(int id, std::vector<cv::Point> line) {
    std::pair<int, std::string> state_res = (id % 2 == 1) 
        ? std::make_pair(id + 1, "entry") 
        : std::make_pair(id - 1, "exit");
    LineInfo lineInfo{id, 0, state_res.first, state_res.second, line};
    lineInfos_.insert({id, lineInfo});
    return true;
}

bool LineState::remove(int id) {
    return true; // TODO
}

bool LineState::update() {
    return true;
}