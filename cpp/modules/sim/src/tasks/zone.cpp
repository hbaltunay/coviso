#include "cv/sim/core.hpp"
#include "cv/sim/tasks.hpp"

int ZoneTask::getZoneValue(cv::Point2f coord) {
    int zoneValue = static_cast<int>(mask_.at<uchar>(
        static_cast<int>(coord.y), 
        static_cast<int>(coord.x)));
    return zoneValue;
}


void ZoneTask::assignRandomTarget(const std::shared_ptr<AgentZData>& agentData) {
    int targetNum = agentData->rng.uniformInt(0, zonesList_.size());
    if (targetNum == 0) {
        agentData->moveData.targetCoord = {
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.width - 1 )), 
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.height - 1))};
    } else {
        int targetCoordNum = agentData->rng.uniformInt(0, coordinateMask[targetNum].size() - 1);
        agentData->moveData.targetCoord = coordinateMask[targetNum][targetCoordNum];
    }
    agentData->targetZone = getZoneValue(agentData->moveData.targetCoord);
    agentData->moveData.arrived = false;
}

bool ZoneTask::init(TaskData taskData) {

    agentNum_ = taskData.agentNum;
    seed_ = taskData.seed;
    fps_ = taskData.fps;
    imgsz_ = taskData.imgsz;
    zones_ = taskData.coorData;

    bool success = createMask();
    if (!success) return false;

    float maxSpeed = std::max(imgsz_.width, imgsz_.height) / (static_cast<float>(fps_) * 10.0f);

    for (int i = 1; i <= agentNum_; ++i) {
        std::string nameAgent = "Agent_Zone_" + std::to_string(i);

        auto agentData = std::make_shared<AgentZData>();
        agentData->moveData.maxSpeed = maxSpeed;
        agentData->moveData.maxAcceleration = 0.2f;
        agentData->rng = Rng(seed_, i);

        agentData->moveData.currentCoord = {
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.width - 1 )), 
            static_cast<float>(agentData->rng.uniformInt(0, imgsz_.height - 1))};

        assignRandomTarget(agentData);

        addAgent(std::make_unique<Agent>(nameAgent, i, this));
        this->addAgentData<AgentZData>(nameAgent, agentData);
    }

    return true;
}

bool ZoneTask::createMask() {
    mask_.create(imgsz_, CV_8UC1); 
    mask_.setTo(0); 

    int zoneId = 1;
    constexpr int MAX_ZONE_ID = 255;

    for (const auto& [zoneName, zoneMap] : zones_) {
        if (zoneMap.find("zone") == zoneMap.end()) [[unlikely]] {
            continue; 
        }

        const auto& zonePointsRaw = zoneMap.at("zone");
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

        std::vector<std::vector<cv::Point>> currentZone = { std::move(zonePoints) };            

        cv::fillPoly(mask_, currentZone, cv::Scalar(zoneId));

        cv::Mat zoneMask = cv::Mat::zeros(mask_.size(), mask_.type());
        cv::fillPoly(zoneMask, currentZone, cv::Scalar(zoneId));

        cv::Mat exactValueMask;
        cv::compare(zoneMask, zoneId, exactValueMask, cv::CMP_EQ);

        cv::Mat innerMask;
        // cv::Mat crossKernel = cv::getStructuringElement(cv::MORPH_CROSS, cv::Size(3, 3));
        cv::erode(exactValueMask, innerMask, cv::Mat());

        std::vector<cv::Point> targetCoordinates;
        cv::findNonZero(innerMask, targetCoordinates);

        coordinateMask[zoneId] = targetCoordinates;

        zonesList_.emplace_back(std::move(zoneName), std::move(currentZone));

        zoneId++;

        if (zoneId > MAX_ZONE_ID) {
            LOG_WARN("Zone limit reached!");    
            return true;
        }
    }

    zoneNum_ = zoneId - 1;

    return true;
}

std::vector<Detection> ZoneTask::generate() {
    std::vector<Detection> detectionList;

    for (int i = 0; i <= zoneNum_; i++) zoneInfo_[i] = 0; 

    for (const auto& agent: getAgents()) {
        Detection detection = agent->run();
        detectionList.push_back(detection);
    }

    return detectionList;
}

void ZoneTask::calculate(AgentInfo& agentInfo) {
    auto d = this->getAgentData<AgentZData>(agentInfo.name);

    if (d->moveData.arrived) assignRandomTarget(d);

    Movement::move(d->moveData);

    d->currentZone = getZoneValue(d->moveData.currentCoord);

    zoneInfo_[d->currentZone]++;

    agentInfo.detection.bbox.x = d->moveData.currentCoord.x;
    agentInfo.detection.bbox.y = d->moveData.currentCoord.y;
}

void ZoneTask::drawCanvas(cv::Mat& canvas) {
    for (const auto& [zoneName, zone] : zonesList_) {
        cv::fillPoly(canvas, zone, cv::Scalar(128, 128, 128));
    }
}

void ZoneTask::drawCanvasStatus(cv::Mat& canvas) {
    int startX = 15;
    int startY = 30;
    int lineSpacing = 25;

    for (int zoneId = 0; zoneId <= zoneNum_; zoneId++) {
        int count = zoneInfo_[zoneId]; 
        std::string text = "Zone " + std::to_string(zoneId) + ": " + std::to_string(count);

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
