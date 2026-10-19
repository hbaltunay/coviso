#include <iostream>

#include "cv/solution/zone.hpp"


ZoneTracker::ZoneTracker(std::filesystem::path configPath, std::string strategy)
    : BaseSolution(configPath), strategy_(strategy) {

    if (strategy_ == "tracked") {
        activeStrategy = &ZoneTracker::trackedStrategy;
    } else {
        activeStrategy = &ZoneTracker::plainStrategy;
    }
}

ZoneTracker::~ZoneTracker() {}

bool ZoneTracker::init() {
    Config config(configPath_);
    if (!config.load()) return false;

    name_ = config.get_or<std::string>("name", "");
    if (name_.empty()) return false;

    imgsz_ = config.get_or<cv::Size>("imgsz", cv::Size(0, 0));
    if (imgsz_.area() <= 0) return false;

    zones_ = config.get_or<CoordinateData>("points", {});
    if (zones_.empty()) return false;

    return createMask();
}

bool ZoneTracker::createMask() {
    mask_ = cv::Mat::zeros(imgsz_, CV_8UC1); 

    int zoneId = 1;
    constexpr int MAX_ZONE_ID = 255;

    for (const auto& [zoneName, zoneMap] : zones_) {
        auto it = zoneMap.find("zone");
        if (it == zoneMap.end()) {
            continue; 
        }

        const auto& zonePointsRaw = it->second;

        std::vector<cv::Point> zonePoints;
        zonePoints.reserve(zonePointsRaw.size()); 

        for (const auto& pt : zonePointsRaw) {
            if (pt.size() == 2 && 
                pt[0] >= 0 && pt[0] < imgsz_.width && 
                pt[1] >= 0 && pt[1] < imgsz_.height) 
            {
                zonePoints.emplace_back(pt[0], pt[1]);
            }
        }
        
        if (zonePoints.size() < 3) continue;

        state_.add(zoneId, zonePoints);

        std::vector<std::vector<cv::Point>> currentZone = { std::move(zonePoints) };            

        cv::fillPoly(mask_, currentZone, cv::Scalar(zoneId));

        zoneId++;

        if (zoneId > MAX_ZONE_ID) {
            LOG_WARN("Zone limit reached!");
            return true;
        }
    }

    state_.add(0, {});
    zoneNum_ = zoneId - 1;

    return true;
}

void ZoneTracker::plainStrategy(std::vector<Detection> detections) {
    std::unordered_map<int, int> zoneFreq;

    for (Detection det : detections) {
        const int x = static_cast<int>(det.bbox.x);
        const int y = static_cast<int>(det.bbox.y);

        if (x < 0 || x >= mask_.cols || y < 0 || y >= mask_.rows) [[unlikely]] {
            continue;
        }

        uchar value_byte = mask_.at<uchar>(y, x);
        int value = static_cast<int>(value_byte);
        zoneFreq[value]++;
    }
    state_.updatePlain(zoneFreq);

}

void ZoneTracker::trackedStrategy(std::vector<Detection> detections) {

    auto& zoneInfos = state_.zoneInfos_;

    for (Detection det : detections) {
        const int x = static_cast<int>(det.bbox.x);
        const int y = static_cast<int>(det.bbox.y);
        int trackId = det.id;

        if (x < 0 || x >= mask_.cols || y < 0 || y >= mask_.rows) [[unlikely]] {
            continue;
        }

        uchar value_byte = mask_.at<uchar>(y, x);
        int value = static_cast<int>(value_byte);

        zoneInfos[value].inZone.push_back(trackId);
    }

    state_.updateTracked();
}

void ZoneTracker::process(cv::Mat& image, std::vector<Detection> detections) {
    (this->*activeStrategy)(detections);
    draw(image, detections);
}

void ZoneTracker::draw(cv::Mat& image, std::vector<Detection> detections) {
    for (const auto& [id, zoneInfo] : state_.zoneInfos_) {
        if (id == 0) continue;
        cv::Scalar color = cv::Scalar(id, id, id);
        cv::fillPoly(image, zoneInfo.zone, cv::Scalar(id));
    }
}

std::vector<std::string> ZoneTracker::getStateInfoStr() {
    return state_.summary();
}