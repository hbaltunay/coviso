#include "cv/core/types.hpp"
#include "cv/sim/core.hpp"


int main() {
    cvs::logInit();

    Size<int> imgsz(1280, 720);

    Simulator sim(imgsz);

    // std::string configPath = "config/zone_config.json";
    std::string configPath = "config/line_config.json";

    sim.addTaskConfig("Test", configPath);

    sim.run();

    return 0;
}