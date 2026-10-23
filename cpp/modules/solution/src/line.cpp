#include "cv/solution/line.hpp"
#include "cv/solution/draw.hpp"


LineTracker::LineTracker(std::filesystem::path configPath)
    : BaseSolution(configPath), state_(imgsz_) {}

LineTracker::~LineTracker() {}

bool LineTracker::init() {
    name_ = config_.get_or<std::string>("name", "");
    if (name_.empty()) return false;

    lines_ = config_.get_or<CoordinateData>("points", {});
    if (lines_.empty()) return false;

    return createMask();
}


std::vector<std::vector<cv::Point>> LineTracker::createLineZones(cv::Point firstPoint, cv::Point secondPoint, float width, float angle) {
    float dx = static_cast<float>(secondPoint.x - firstPoint.x);
    float dy = static_cast<float>(secondPoint.y - firstPoint.y);
    float lineLength = std::sqrt(dx * dx + dy * dy);

    if (lineLength < 0.001f) return {};

    float baseAngleRad = std::atan2(dy, dx);

    float offsetAngleRad = (angle * 3.14159265f) / 180.0f;
    float finalAngleRad = baseAngleRad + offsetAngleRad;

    float shiftX = width * std::cos(finalAngleRad);
    float shiftY = width * std::sin(finalAngleRad);
    cv::Point2f shiftVectorA(shiftX, shiftY);

    cv::Point2f shiftVectorB = -shiftVectorA;

    std::vector<cv::Point> lineEntry = {
        firstPoint,
        secondPoint,
        cv::Point(static_cast<int>(secondPoint.x + shiftVectorA.x), 
                  static_cast<int>(secondPoint.y + shiftVectorA.y)),
        cv::Point(static_cast<int>(firstPoint.x + shiftVectorA.x), 
                  static_cast<int>(firstPoint.y + shiftVectorA.y))
    };

    std::vector<cv::Point> lineExit = {
        firstPoint,
        secondPoint,
        cv::Point(static_cast<int>(secondPoint.x + shiftVectorB.x), 
                  static_cast<int>(secondPoint.y + shiftVectorB.y)),
        cv::Point(static_cast<int>(firstPoint.x + shiftVectorB.x), 
                  static_cast<int>(firstPoint.y + shiftVectorB.y))
    };

    std::vector<std::vector<cv::Point>> result = { lineEntry, lineExit};

    return result;
}


bool LineTracker::createMask() {
    mask_ = cv::Mat::zeros(imgsz_, CV_8UC1);

    int lineId = 1;
    constexpr int MAX_LINE_ID = 254;

    for (const auto& [lineName, lineMap] : lines_) {
        if (lineMap.find("line") == lineMap.end()) [[unlikely]] {
            continue; 
        }

        const auto& linePointsRaw = lineMap.at("line");
        std::vector<cv::Point> linePoints;
        linePoints.reserve(linePointsRaw.size());

        if (linePointsRaw.size() != 3 ) return false;    
        
        cv::Point firstPoint, secondPoint;
        float w = 0.0f;
        float a = 0.0f;

        for (int i = 0; i < 3; i++) {
            const auto& pt = linePointsRaw[i];
            if (i < 2) {
                if (pt.size() == 2 && 
                    pt[0] >= 0 && pt[0] < imgsz_.width && 
                    pt[1] >= 0 && pt[1] < imgsz_.height){
                    linePoints.emplace_back(pt[0], pt[1]);

                    if (i == 0) {
                        firstPoint = cv::Point(pt[0], pt[1]);
                    } else {
                        secondPoint = cv::Point(pt[0], pt[1]);
                    }
                }
            } else {
                if (pt.size() == 2 && 
                    pt[0] >= 0 && pt[0] < std::max(imgsz_.width, imgsz_.height) && 
                    pt[1] >= 45 && pt[1] <= 135){
                    linePoints.emplace_back(pt[0], pt[1]);
                    w = static_cast<float>(pt[0]);
                    a = static_cast<float>(pt[1]);
                }
            }
        }

        
        if (linePoints.size() != 3) continue;
        
        std::vector<std::vector<cv::Point>> lineZones = createLineZones(firstPoint, secondPoint, w, a);
        
        for (const auto& lineZone : lineZones) {
            std::vector<std::vector<cv::Point>> currentZone = { std::move(lineZone) };            
            
            cv::fillPoly(mask_, currentZone, cv::Scalar(lineId));
            
            state_.add(lineId, lineZone);
            
            lineId++;
        }

        if (lineId > MAX_LINE_ID) {
            LOG_WARN("Line limit reached!");
            return true;
        };
    }

    lineNum_ = lineId;

    return true;
}

void LineTracker::process(cv::Mat& image, std::vector<Detection> detections) {
    auto& lineInfos = state_.lineInfos_;

    for (Detection& det : detections) {
        const int x = static_cast<int>(det.bbox.x);
        const int y = static_cast<int>(det.bbox.y);
        int trackId = det.trackId;

        if (x < 0 || x >= mask_.cols || y < 0 || y >= mask_.rows) [[unlikely]] {
            continue;
        }

        uchar value_byte = mask_.at<uchar>(y, x);
        int value = static_cast<int>(value_byte);

        auto& t = state_.trackInfos[trackId];

        t.currentLine = value;

        if (t.currentLine != t.lastLine) {
            if (t.passedNum == 0) {
                t.passedNum = (t.lastLine > 0) ? t.lastLine : t.currentLine;
            } else if (!t.passed && t.currentLine == 0) {
                t.passedNum = 0;
            } else if (t.passed && t.currentLine == 0) {
                int passedLine = lineInfos.at(t.lastLine).lineNum;
                lineInfos.at(passedLine).count++;
                t.passed = false;
                t.passedNum = 0;
            } else if (t.currentLine == t.passedNum) {
                t.passed = false;
            } else if (t.lastLine == lineInfos.at(t.currentLine).lineNum) {
                t.passed = true;
            } else {
                LOG_ERROR("Invalid action performed.");
            }
        }
        t.lastLine = t.currentLine;
    }

    state_.update();
    draw(image);
}

void LineTracker::draw(cv::Mat& image) {
    drawLine(image, state_.infos());
}

std::vector<std::string> LineTracker::getStateInfoStr() {
    return state_.summary();
}