#include <fstream>
#include <nlohmann/json.hpp>

#include "cv/tool/config.hpp"
#include "cv/tool/logger.hpp"

using json = nlohmann::json;


struct Config::Impl {
    std::filesystem::path configPath;
    json configJson;
};

Config::Config() : impl_(std::make_unique<Impl>()) {}

Config::Config(const std::filesystem::path& configPath)
    : impl_(std::make_unique<Impl>()) {
    impl_->configPath = configPath;
}

Config::~Config() {}

bool Config::load() {
    const auto& path = impl_->configPath;

    if (!std::filesystem::exists(path)) {
        LOG_ERROR("Config file not found: {}", path.string());
        return false;
    }

    try {
        std::ifstream file(path);
        if (!file.is_open()) {
            LOG_ERROR("Failed to open config file: {}", path.string());
            return false;
        }
        file >> impl_->configJson;
    }
    catch (const json::parse_error& e) {
        LOG_ERROR("JSON parse error in config file {}: {}", path.string(), e.what());
        return false;
    }
    catch (const std::exception& e) {
        LOG_ERROR("Unexpected error while reading config file: {}", e.what());
        return false;
    }

    LOG_INFO("Config file loaded successfully: {}", path.string());
    return true;
}

bool Config::contains(const std::string& key) const {
    return impl_->configJson.contains(key);
}

namespace {
template <typename T>
void readAs(const json& j, const std::string& key, T& out) {
    out = j.at(key).get<T>();
}
}

void Config::read(const std::string& k, int& out) const                      { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, double& out) const                   { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, bool& out) const                     { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, std::string& out) const              { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, std::vector<int>& out) const         { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, std::vector<double>& out) const      { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, std::vector<std::string>& out) const { readAs(impl_->configJson, k, out); }
void Config::read(const std::string& k, CoordinateData& out) const           { readAs(impl_->configJson, k, out); }

void Config::read(const std::string& k, Size<int>& out) const {
    const auto& node = impl_->configJson.at(k);
    node.at("width").get_to(out.width);
    node.at("height").get_to(out.height);
}