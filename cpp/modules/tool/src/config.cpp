#include "cv/tool/logger.hpp"
#include "cv/tool/config.hpp"
#include <fstream>

Config::Config(const std::filesystem::path& configPath) 
    : configPath_(configPath) {}

bool Config::load() {
    if (!std::filesystem::exists(configPath_)) {
        LOG_ERROR("Config file not found: {}", configPath_.string());
        return false;
    }

    try {
        std::ifstream file(configPath_);
        if (!file.is_open()) {
            LOG_ERROR("Failed to open config file: {}", configPath_.string());
            return false;
        }

        file >> configJson_;
    } 
    catch (const nlohmann::json::parse_error& e) {
        LOG_ERROR("JSON parse error in config file {}: {}", configPath_.string(), e.what());
        return false;
    }
    catch (const std::exception& e) {
        LOG_ERROR("Unexpected error while reading config file: {}", e.what());
        return false;
    }

    LOG_INFO("Config file loaded successfully: {}", configPath_.string());
    return true;
}