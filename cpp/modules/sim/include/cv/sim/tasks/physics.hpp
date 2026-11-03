#pragma once

#include "cv/core/types.hpp"


struct MoveData {
    Point2f targetCoord, currentCoord;
    Point2f currentVel{0.f, 0.f};
    bool arrived = false;
    float maxSpeed;
    float maxAcceleration;
    double currentSpeed = 0;
};

class Movement {
public:
    static void move(MoveData& moveData);
};