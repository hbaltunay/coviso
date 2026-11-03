#pragma once

#include <filesystem>
#include <memory>
#include <string>
#include <type_traits>
#include <vector>

#include "cv/core/types.hpp"
#include "cv/tool/export.h"


class CVS_EXPORT Config {
public:
    Config();
    explicit Config(const std::filesystem::path& configPath);
    ~Config();

    bool load();
    bool contains(const std::string& key) const;

    template <typename T>
    T get(const std::string& key) const {
        T value{};
        read(key, value);
        return value;
    }

    template <typename T>
    T get_or(const std::string& key, const T& defaultValue) const {
        T value = defaultValue;
        if (contains(key)) {
            read(key, value);
        }
        return value;
    }

private:
    void read(const std::string& key, int& out) const;
    void read(const std::string& key, double& out) const;
    void read(const std::string& key, bool& out) const;
    void read(const std::string& key, std::string& out) const;
    void read(const std::string& key, std::vector<int>& out) const;
    void read(const std::string& key, std::vector<double>& out) const;
    void read(const std::string& key, std::vector<std::string>& out) const;
    void read(const std::string& key, Size<int>& out) const;
    void read(const std::string& key, CoordinateData& out) const;

    struct Impl;
    std::unique_ptr<Impl> impl_;
};