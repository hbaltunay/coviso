#include <stdexcept>

#include "cv/solution/base.hpp"
#include "cv/solution/draw.hpp"


BaseSolution::BaseSolution(std::filesystem::path configPath)
    : configPath_(configPath) {
    
    config_ = std::make_unique<Config>(configPath_);

    if (!config_->load()) throw std::runtime_error("Config could not be loaded.");

    imgsz_ = config_->get_or<Size<int>>("imgsz", Size<int>(0, 0));
    if (imgsz_.area() <= 0) throw std::runtime_error("Invalid imgsz");
}