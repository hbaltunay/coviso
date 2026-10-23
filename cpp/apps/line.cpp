#include "cv/sim/core.hpp"
#include "cv/sim/tasks.hpp"
#include "cv/solution/line.hpp"


void onMouse(int event, int x, int y, int flags, void* userdata) {
    Simulator* sim = reinterpret_cast<Simulator*>(userdata);

    if (event == cv::EVENT_LBUTTONDOWN) {
        for (const auto& [name, task] : sim->tasks_) {
            for (auto& [agentName, agentData] : task->getAgentMap()) {
                auto data = std::static_pointer_cast<AgentLData>(agentData);

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

    std::string configPath = "config/line_config.json";

    sim.addTaskConfig("Test", configPath);

    LineTracker tracker(configPath);
    tracker.init();

    std::string windowName = "Simulator";
    cv::namedWindow(windowName, cv::WINDOW_GUI_NORMAL);
    cv::setMouseCallback(windowName, onMouse, &sim);
    cv::resizeWindow(windowName, 800, 600);

    cv::Mat org_canvas = cv::imread("canvas.jpg");
    cv::Mat canvas;
    cv::resize(org_canvas, canvas, cv::Size(1280, 720), 0, 0, cv::INTER_LINEAR);

    while (true) {
        cv::Mat display_canvas;

        canvas.copyTo(display_canvas);

        for (const auto& [name, task]: sim.tasks_) {
            std::vector<Detection> detectionList = task->generate();

            tracker.process(display_canvas, detectionList);
            
            sim.draw(display_canvas, detectionList);
            sim.writeState(display_canvas, tracker.getStateInfoStr());
        }
        
        cv::imshow(windowName, display_canvas);

        if (cv::waitKey(33) == 27) break;
    }

    return 0;
}