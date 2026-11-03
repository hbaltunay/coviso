#include "cv/tool/logger.hpp"

#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/rotating_file_sink.h>

namespace cvs {

void logInit() {
    static std::once_flag init_flag;
    std::call_once(init_flag, []() {
        // if (!std::filesystem::exists("logs")) {
        //     std::filesystem::create_directories("logs");
        // }

        auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
        // auto file_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
            // "logs/cvs.log", 1024 * 1024 * 10, 5);

        // std::vector<spdlog::sink_ptr> sinks{console_sink, file_sink};
        std::vector<spdlog::sink_ptr> sinks{console_sink};

        auto logger = std::make_shared<spdlog::logger>("main", sinks.begin(), sinks.end());

        logger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%3!l%$] [%t] %v");
        logger->set_level(spdlog::level::trace);
        logger->flush_on(spdlog::level::warn);

        spdlog::set_default_logger(logger);

        LOG_INFO("Logger has been configured.");
    });
}

void setLogLevel(LogLevel level) {
    spdlog::level::level_enum l = spdlog::level::info;
    switch (level) {
        case LogLevel::Trace:    l = spdlog::level::trace;    break;
        case LogLevel::Debug:    l = spdlog::level::debug;    break;
        case LogLevel::Info:     l = spdlog::level::info;     break;
        case LogLevel::Warn:     l = spdlog::level::warn;     break;
        case LogLevel::Error:    l = spdlog::level::err;      break;
        case LogLevel::Critical: l = spdlog::level::critical; break;
        case LogLevel::Off:      l = spdlog::level::off;      break;
    }
    spdlog::set_level(l);
}

namespace detail {

#define CVS_DEFINE_LEVEL(name, spd_level)                                      \
    bool is_##name##_enabled() {                                               \
        auto* logger = spdlog::default_logger_raw();                           \
        return logger && logger->should_log(spd_level);                        \
    }                                                                          \
    void write_##name(std::string_view msg) {                                  \
        auto* logger = spdlog::default_logger_raw();                           \
        if (!logger) return;                                                   \
        logger->log(spd_level, spdlog::string_view_t(msg.data(), msg.size())); \
    }

CVS_DEFINE_LEVEL(trace,    spdlog::level::trace)
CVS_DEFINE_LEVEL(debug,    spdlog::level::debug)
CVS_DEFINE_LEVEL(info,     spdlog::level::info)
CVS_DEFINE_LEVEL(warn,     spdlog::level::warn)
CVS_DEFINE_LEVEL(error,    spdlog::level::err)
CVS_DEFINE_LEVEL(critical, spdlog::level::critical)

#undef CVS_DEFINE_LEVEL

} // namespace detail
} // namespace cvs