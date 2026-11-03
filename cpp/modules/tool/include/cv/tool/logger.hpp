#pragma once

#include <sstream>
#include <string>
#include <string_view>

#include "cv/tool/export.h"

namespace cvs {

enum class LogLevel { Trace, Debug, Info, Warn, Error, Critical, Off };

CVS_EXPORT void logInit();

CVS_EXPORT void setLogLevel(LogLevel level);

namespace detail {

#define CVS_DECLARE_LEVEL(name)                         \
    CVS_EXPORT bool is_##name##_enabled();              \
    CVS_EXPORT void write_##name(std::string_view msg);

CVS_DECLARE_LEVEL(trace)
CVS_DECLARE_LEVEL(debug)
CVS_DECLARE_LEVEL(info)
CVS_DECLARE_LEVEL(warn)
CVS_DECLARE_LEVEL(error)
CVS_DECLARE_LEVEL(critical)

#undef CVS_DECLARE_LEVEL

template <LogLevel L> struct level_traits;

#define CVS_LEVEL_TRAITS(Level, name)                              \
    template <> struct level_traits<LogLevel::Level> {             \
        static bool enabled() { return is_##name##_enabled(); }    \
        static void write(std::string_view m) { write_##name(m); } \
    };

CVS_LEVEL_TRAITS(Trace,    trace)
CVS_LEVEL_TRAITS(Debug,    debug)
CVS_LEVEL_TRAITS(Info,     info)
CVS_LEVEL_TRAITS(Warn,     warn)
CVS_LEVEL_TRAITS(Error,    error)
CVS_LEVEL_TRAITS(Critical, critical)

#undef CVS_LEVEL_TRAITS

inline void formatTo(std::ostringstream& os, std::string_view fmt) {
    os << fmt;
}

template <typename T, typename... Rest>
void formatTo(std::ostringstream& os, std::string_view fmt,
               const T& value, const Rest&... rest) {
    const auto pos = fmt.find("{}");
    if (pos == std::string_view::npos) {
        os << fmt;
        return;
    }
    os << fmt.substr(0, pos) << value;
    formatTo(os, fmt.substr(pos + 2), rest...);
}

} // namespace detail

template <LogLevel L, typename... Args>
void log(std::string_view fmt, const Args&... args) {
    using traits = detail::level_traits<L>;
    if (!traits::enabled()) return;
    std::ostringstream os;
    detail::formatTo(os, fmt, args...);
    traits::write(os.str());
}

} // namespace cvs

#define LOG_TRACE(...)    ::cvs::log<::cvs::LogLevel::Trace>(__VA_ARGS__)
#define LOG_DEBUG(...)    ::cvs::log<::cvs::LogLevel::Debug>(__VA_ARGS__)
#define LOG_INFO(...)     ::cvs::log<::cvs::LogLevel::Info>(__VA_ARGS__)
#define LOG_WARN(...)     ::cvs::log<::cvs::LogLevel::Warn>(__VA_ARGS__)
#define LOG_ERROR(...)    ::cvs::log<::cvs::LogLevel::Error>(__VA_ARGS__)
#define LOG_CRITICAL(...) ::cvs::log<::cvs::LogLevel::Critical>(__VA_ARGS__)