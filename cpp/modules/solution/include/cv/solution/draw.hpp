#pragma once

#include "state.hpp"
#include "cv/tool/logger.hpp"

namespace cv {
class Mat;
}


void drawZone(cv::Mat& image, ZoneState& state);

void drawLine(cv::Mat& image, LineState& state);