#include "cv/solution/draw.hpp"

void drawZone(cv::Mat& image, const std::unordered_map<int, ZoneInfo>& zones) {
    for (auto& [zoneId, zone] : zones) {
        if (zoneId == 0 || !zone.ready) continue;

        cv::Mat roi = image(zone.roi);
        const cv::Mat& overlay = zone.empty ? zone.zeroRoi : zone.oneRoi;
        cv::addWeighted(roi, 0.4, overlay, 0.6, 0.0, zone.blended);
        zone.blended.copyTo(roi, zone.maskRoiU8);
    }
}

void drawLine(cv::Mat& image, const std::unordered_map<int, LineInfo>& lines) {
    for (auto& [lineId, line] : lines) {
        if (!line.ready) continue;

        cv::Mat roi = image(line.roi);
        cv::addWeighted(roi, 0.4, line.lineRoi, 0.6, 0.0, line.blended);
        line.blended.copyTo(roi, line.maskRoiU8);
    }
}