#pragma once

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include "state.hpp"
#include "cv/tool/logger.hpp"


void drawZone(cv::Mat& image, const std::unordered_map<int, ZoneInfo>& zones);

void drawLine(cv::Mat& image, const std::unordered_map<int, LineInfo>& lines);