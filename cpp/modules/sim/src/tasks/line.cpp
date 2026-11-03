#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include "cv/sim/core.hpp"
#include "cv/sim/tasks.hpp"
#include "utils.hpp"

struct LineTask::Impl {
    cv::Mat mask;
};

LineTask::LineTask() : impl_(std::make_unique<Impl>())  {}

LineTask::~LineTask() = default;

cv::Mat LineTask::getMask() { return impl_->mask; }

int LineTask::getLineValue(Point2f coord) {
    int zoneValue = static_cast<int>(impl_->mask.at<uchar>(
        static_cast<int>(coord.y), 
        static_cast<int>(coord.x)));
    return zoneValue;
}


void LineTask::assignRandomTarget(const std::shared_ptr<AgentLData>& agentData) {
    int targetNum = agentData->rng.uniformInt(0, linesList_.size());
    if (targetNum == 0) {
        agentData->moveData.targetCoord = {
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.width - 1 )), 
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.height - 1))};
    } else {
        int targetCoordNum = agentData->rng.uniformInt(0, coordinateMask[targetNum].size() - 1);
        agentData->moveData.targetCoord = coordinateMask[targetNum][targetCoordNum];
    }
    agentData->targetLine = getLineValue(agentData->moveData.targetCoord);
    agentData->moveData.arrived = false;
}

bool LineTask::init(TaskData taskData) {
    agentNum_ = taskData.agentNum;
    seed_ = taskData.seed;
    fps_ = taskData.fps;
    imgsz_ = taskData.imgsz;
    lines_ = taskData.coorData;

    bool success = createMask();
    if (!success) return false;

    float maxSpeed = std::max(imgsz_.width, imgsz_.height) / (static_cast<float>(fps_) * 10.0f);

    for (int i = 1; i <= agentNum_; ++i) {
        std::string nameAgent = "Agent_Line_" + std::to_string(i);

        auto agentData = std::make_shared<AgentLData>();
        agentData->moveData.maxSpeed = maxSpeed;
        agentData->moveData.maxAcceleration = 0.2f;
        agentData->rng = Rng(seed_, i);

        agentData->moveData.currentCoord = {
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.width - 1 )), 
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.height - 1))};

        assignRandomTarget(agentData);

        agentData->currentLine = getLineValue(agentData->moveData.currentCoord);
        agentData->lastLine = getLineValue(agentData->moveData.currentCoord);

        addAgent(std::make_unique<Agent>(nameAgent, i, this));
        this->addAgentData<AgentLData>(nameAgent, agentData);
    }
    return true;
}

std::vector<std::vector<Point2i>> LineTask::createLineZones(Point2i firstPoint, Point2i secondPoint, float width, float angle) {
    float dx = static_cast<float>(secondPoint.x - firstPoint.x);
    float dy = static_cast<float>(secondPoint.y - firstPoint.y);
    float lineLength = std::sqrt(dx * dx + dy * dy);

    if (lineLength < 0.001f) return {};

    float baseAngleRad = std::atan2(dy, dx);

    float offsetAngleRad = (angle * 3.14159265f) / 180.0f;
    float finalAngleRad = baseAngleRad + offsetAngleRad;

    float shiftX = width * std::cos(finalAngleRad);
    float shiftY = width * std::sin(finalAngleRad);
    Point2f shiftVectorA(shiftX, shiftY);

    Point2f shiftVectorB(-shiftX, -shiftY);

    std::vector<Point2i> lineEntry = {
        firstPoint,
        secondPoint,
        Point2i(static_cast<int>(secondPoint.x + shiftVectorA.x), static_cast<int>(secondPoint.y + shiftVectorA.y)),
        Point2i(static_cast<int>(firstPoint.x + shiftVectorA.x), static_cast<int>(firstPoint.y + shiftVectorA.y))
    };

    std::vector<Point2i> lineExit = {
        firstPoint,
        secondPoint,
        Point2i(static_cast<int>(secondPoint.x + shiftVectorB.x), static_cast<int>(secondPoint.y + shiftVectorB.y)),
        Point2i(static_cast<int>(firstPoint.x + shiftVectorB.x), static_cast<int>(firstPoint.y + shiftVectorB.y))
    };

    std::vector<std::vector<Point2i>> result = { lineEntry, lineExit};

    return result;
}

bool LineTask::createMask() {
    impl_->mask.create(imgsz_.height, imgsz_.width, CV_8UC1); 
    impl_->mask.setTo(0); 

    int lineId = 1;
    constexpr int MAX_LINE_ID = 254;

    for (const auto& [lineName, lineMap] : lines_) {
        if (lineMap.find("line") == lineMap.end()) [[unlikely]] {
            continue; 
        }

        const auto& linePointsRaw = lineMap.at("line");
        std::vector<Point2i> linePoints;
        linePoints.reserve(linePointsRaw.size());

        if (linePointsRaw.size() != 3 ) return false;    
        
        Point2i firstPoint, secondPoint;
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
                        firstPoint = Point2i(pt[0], pt[1]);
                    } else {
                        secondPoint = Point2i(pt[0], pt[1]);
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

        std::vector<std::vector<Point2i>> lineZones = createLineZones(firstPoint, secondPoint, w, a);
        
        for (const auto& lineZone : lineZones) {
            std::vector<cv::Point> lineZoneCv = toCv(lineZone);
            std::vector<std::vector<cv::Point>> currentZone = { lineZoneCv };

            cv::fillPoly(impl_->mask, currentZone, cv::Scalar(lineId));

            cv::Mat zoneMask = cv::Mat::zeros(impl_->mask.size(), impl_->mask.type());
            cv::fillPoly(zoneMask, currentZone, cv::Scalar(lineId));

            cv::Mat exactValueMask;
            cv::compare(zoneMask, lineId, exactValueMask, cv::CMP_EQ);

            cv::Mat innerMask;
            // cv::Mat crossKernel = cv::getStructuringElement(cv::MORPH_CROSS, cv::Size(3, 3));
            cv::erode(exactValueMask, innerMask, cv::Mat());

            std::vector<cv::Point2f> targetCoordinatesCv;
            cv::findNonZero(innerMask, targetCoordinatesCv);

            std::vector<Point2f> targetCoordinates = fromCv(targetCoordinatesCv);

            coordinateMask[lineId] = targetCoordinates;

            lineId++;
        }

        LineInfoData lineInfoData{lineName, firstPoint, secondPoint, w, a, { lineZones[0] }, { lineZones[1] }};
        linesInfoList_.emplace_back(lineInfoData);

        std::vector<std::vector<Point2i>> entryLine = { lineZones[0] };
        std::vector<std::vector<Point2i>> exitLine = { lineZones[1] };

        linesList_.emplace_back(std::move(lineName + "_entry"), std::move(entryLine));
        linesList_.emplace_back(std::move(lineName + "_exit"), std::move(exitLine));

        lineInfo_[lineId - 2] = {lineName, "entry", lineId -1, 0};
        lineInfo_[lineId - 1] = {lineName, "exit", lineId - 2,  0};

        if (lineId > MAX_LINE_ID) {
            LOG_WARN("Line limit reached!");
            return true;
        };
    }

    lineNum_ = lineId - 1;

    return true;
}

std::vector<Detection> LineTask::generate() {
    std::vector<Detection> detectionList;

    for (const auto& agent: getAgents()) {
        Detection detection = agent->run();
        detectionList.push_back(detection);
    }

    return detectionList;
}

void LineTask::calculate(AgentInfo& agentInfo) {
    auto d = this->getAgentData<AgentLData>(agentInfo.name);

    if (d->moveData.arrived) assignRandomTarget(d);

    Movement::move(d->moveData);

    d->currentLine = getLineValue(d->moveData.currentCoord);

    if (d->currentLine != d->lastLine) {
        if (d->passedNum == 0) {
            d->passedNum = (d->lastLine > 0) ? d->lastLine : d->currentLine;
        } else if (!d->passed && d->currentLine == 0){
            d->passedNum = 0;
        } else if (d->passed && d->currentLine == 0) {
            int passedLine = lineInfo_.at(d->lastLine).lineNum;
            lineInfo_.at(passedLine).count++;
            d->passed = false;
            d->passedNum = 0;
        } else if (d->currentLine == d->passedNum) {
            d->passed = false;
        } else if (d->lastLine == lineInfo_.at(d->currentLine).lineNum) {
            d->passed = true;
        } else {
            LOG_ERROR("Invalid action performed.");
        }
    }

    d->lastLine = d->currentLine;
    
    agentInfo.detection.bbox.x = d->moveData.currentCoord.x;
    agentInfo.detection.bbox.y = d->moveData.currentCoord.y;
}

void LineTask::drawCanvas(cv::Mat& canvas) {
    for (const auto& line : linesInfoList_) {
        std::vector<cv::Point> entryZone = toCv(line.entryZone[0]);
        std::vector<cv::Point> exitZone = toCv(line.exitZone[0]);   
        cv::fillPoly(canvas, {entryZone}, cv::Scalar(96, 96, 96));
        cv::fillPoly(canvas, {exitZone}, cv::Scalar(160, 160, 160));
    }
}

void LineTask::drawCanvasStatus(cv::Mat& canvas) {
    int startX = 15;
    int startY = 30;
    int lineSpacing = 25;

    for (int lineId = 1; lineId <= lineNum_; lineId++) {
        LinePassedInfo info = lineInfo_.at(lineId); 
        std::string text = info.lineName + "-" + info.lineType + " : " + std::to_string(info.count);

        cv::putText(canvas, 
                    text, 
                    cv::Point(startX, startY), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    0.9,
                    cv::Scalar(255, 255, 255),
                    1,
                    cv::LINE_AA);

        startY += lineSpacing;
    }
}
