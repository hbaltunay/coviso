#include "cv/solution/draw.hpp"

void drawZone(cv::Mat& image, ZoneState& state) {
    state.draw(image);
}

void drawLine(cv::Mat& image, LineState& state) {
    state.draw(image);
}