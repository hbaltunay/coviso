#include <opencv2/core.hpp>

#include "cv/sim/core.hpp"
#include "cv/sim/tasks.hpp"

void onMouse(int event, int x, int y, int flags, void* userdata) {
    Simulator* sim = reinterpret_cast<Simulator*>(userdata);

    if (event == cv::EVENT_LBUTTONDOWN) {
        for (const auto& [name, task] : sim->tasks_) {
            for (auto& [agentName, agentData] : task->getAgentMap()) {
                auto data = std::static_pointer_cast<AgentZData>(agentData);

                if (data != nullptr) {
                    MoveData& movedata = data->moveData;
                    movedata.targetCoord = cv::Point2f(static_cast<float>(x), static_cast<float>(y));
                }
            }
        }
    }
}

int main() {
    Logger::init();

    cv::Point imgsz(1280, 720);

    Simulator sim(imgsz);

    sim.addTaskConfig("Test", "config/zone_config.json");

    std::string windowName = "Simulator";
    cv::namedWindow(windowName, cv::WINDOW_GUI_NORMAL);
    cv::setMouseCallback(windowName, onMouse, &sim);

    while (true) {
        cv::Mat display_canvas;
        sim.canvas_.copyTo(display_canvas);

        for (const auto& [name, task]: sim.tasks_) {
            std::vector<Detection> detectionList = task->generate();

            for (const auto& detection : detectionList) {
                cv::circle(display_canvas, cv::Point(detection.bbox.x, detection.bbox.y),
                           5, cv::Scalar(255), cv::FILLED, cv::LINE_AA);
            }

            task->drawCanvasStatus(display_canvas);
        }

        cv::imshow(windowName, display_canvas);

        if (cv::waitKey(33) == 27) break;
    }

    return 0;
}