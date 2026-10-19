#include "cv/sim/tasks/physics.hpp"


void Movement::move(MoveData& moveData) {
    // 1. Calculate direction and distance vector to the target
    cv::Point2f to_target = moveData.targetCoord - moveData.currentCoord;
    float distance = static_cast<float>(cv::norm(to_target));
    
    // Stop movement and snap to target if we are close enough (tolerance)
    if (distance < 0.5f) {
        moveData.currentCoord = moveData.targetCoord;
        moveData.currentVel = cv::Point2f(0.f, 0.f);
        moveData.currentSpeed = 0.0;
        moveData.arrived = true;
        return;
    }
    
    // Unit direction vector
    cv::Point2f direction = to_target / distance;
    
    // 2. Calculate braking distance (Frame-based timeless velocity formula)
    float braking_distance = (moveData.currentSpeed * moveData.currentSpeed) / (2.0f * moveData.maxAcceleration);
    
    // 3. Determine target speed
    float target_speed = 0.0f;
    if (distance > braking_distance) {
        target_speed = moveData.maxSpeed; // Distance is enough, accelerate to max speed
    } else {
        target_speed = std::sqrt(2.0f * moveData.maxAcceleration * distance); // Decelerate to stop exactly at target
    }
    
    // 4. Acceleration / Velocity adjustment
    cv::Point2f target_velocity = direction * target_speed;
    cv::Point2f velocity_error = target_velocity - moveData.currentVel;
    float error_len = static_cast<float>(cv::norm(velocity_error));
    
    if (error_len > 0.01f) {
        cv::Point2f accel_dir = velocity_error / error_len;
        
        // If required velocity change is smaller than acceleration limit, snap to target velocity
        if (moveData.maxAcceleration > error_len) {
            moveData.currentVel = target_velocity;
        } else {
            moveData.currentVel += accel_dir * moveData.maxAcceleration; // Apply acceleration step
        }
    } else {
        moveData.currentVel = target_velocity;
    }
    
    // Update scalar speed and current coordinates
    moveData.currentSpeed = cv::norm(moveData.currentVel);
    moveData.currentCoord += moveData.currentVel;
}