#pragma once

#include <opencv2/core.hpp>


struct MoveData {
    cv::Point2f targetCoord, currentCoord;
    cv::Point2f currentVel{0.f, 0.f};
    bool arrived = false;
    float maxSpeed;
    float maxAcceleration;
    double currentSpeed = 0;
};

class Movement {
public:
    static void move(MoveData& moveData);
};