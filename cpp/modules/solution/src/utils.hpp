#pragma once

#include <opencv2/core.hpp>
#include <vector>

#include "cv/core/types.hpp"

template <typename T>
cv::Point_<T> toCv(const Point<T>& p) {
    return cv::Point_<T>(p.x, p.y);
}

template <typename T>
std::vector<cv::Point_<T>> toCv(const std::vector<Point<T>>& src) {
    std::vector<cv::Point_<T>> dst;
    dst.reserve(src.size());
    for (const auto& p : src)
        dst.emplace_back(p.x, p.y);
    return dst;
}

template <typename T>
Point<T> fromCv(const cv::Point_<T>& p) {
    return Point<T>(p.x, p.y);
}

template <typename T>
std::vector<Point<T>> fromCv(const std::vector<cv::Point_<T>>& src) {
    std::vector<Point<T>> dst;
    dst.reserve(src.size());
    for (const auto& p : src)
        dst.emplace_back(p.x, p.y);
    return dst;
}