#pragma once

#include <cmath>
#include <string>
#include <map>
#include <vector>
#include <type_traits>


template <typename T>
struct Size {
    T width;
    T height;

    Size(): width(0), height(0) {}

    Size(T w, T h) : width(w), height(h) {}

    T area() { return width * height; }
};


template <typename T>
struct Point {
    T x;
    T y;

    Point() : x(0), y(0) {}
    Point(T p1, T p2) : x(p1), y(p2) {}

    Point& operator+=(const Point& o) { x += o.x; y += o.y; return *this; }
    Point& operator-=(const Point& o) { x -= o.x; y -= o.y; return *this; }
    Point& operator*=(T s)            { x *= s;   y *= s;   return *this; }
    Point& operator/=(T s)            { x /= s;   y /= s;   return *this; }

    Point operator-() const { return Point(-x, -y); }

    T dot(const Point& o) const   { return x * o.x + y * o.y; }
    T cross(const Point& o) const { return x * o.y - y * o.x; }
    T norm2() const               { return x * x + y * y; }

    double norm() const { return std::sqrt(static_cast<double>(norm2())); }
};

template <typename T>
Point<T> operator+(Point<T> a, const Point<T>& b) { return a += b; }

template <typename T>
Point<T> operator-(Point<T> a, const Point<T>& b) { return a -= b; }

template <typename T>
Point<T> operator*(Point<T> p, T s) { return p *= s; }

template <typename T>
Point<T> operator*(T s, Point<T> p) { return p *= s; }

template <typename T>
Point<T> operator/(Point<T> p, T s) { return p /= s; }

template <typename T>
bool operator==(const Point<T>& a, const Point<T>& b) { return a.x == b.x && a.y == b.y; }

template <typename T>
bool operator!=(const Point<T>& a, const Point<T>& b) { return !(a == b); }

template <typename T>
double distance(const Point<T>& a, const Point<T>& b) { return (a - b).norm(); }

using Coordinate2D = std::vector<int>;
using CoordinateList = std::vector<Coordinate2D>;
using InnerMap = std::map<std::string, CoordinateList>;
using CoordinateData = std::map<std::string, InnerMap>;

using Point2i = Point<int>;
using Point2f = Point<float>;