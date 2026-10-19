#pragma once

#include <map>
#include <string>
#include <vector>
#include <filesystem>
#include <string>
#include <opencv2/core.hpp>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace cv {
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Size, width, height)
}

class Config {
public:
    explicit Config(const std::filesystem::path& configPath);

    [[nodiscard]] bool load();

    template <typename T>
    T get(const std::string& key) const {
        return configJson_.at(key).get<T>();
    }

    template <typename T>
    T get_or(const std::string& key, const T& defaultValue) const {
        if (!configJson_.contains(key)) {
            return defaultValue;
        }
        return configJson_.value(key, defaultValue);
    }

private:
    std::filesystem::path configPath_;
    json configJson_;
};