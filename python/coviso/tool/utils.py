import logging


class LoggerDisableLevel:
    def __init__(self, name: str, level: str = "WARNING") -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self.level = level
        self.default_level = None

    def __enter__(self) -> None:
        self.default_level = self.logger.level
        self.logger.setLevel(self.level)

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa
        self.logger.setLevel(self.default_level)


class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    INVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"

    # Foreground — normal
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Foreground — bright
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background — normal
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Background — bright
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"


LEVEL_COLORS = {
    logging.INFO: ANSI.GREEN,
    logging.WARNING: ANSI.YELLOW,
    logging.ERROR: ANSI.RED,
    logging.DEBUG: ANSI.CYAN,
}


class LogTypeFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        color = LEVEL_COLORS.get(record.levelno, ANSI.BLUE)
        name = record.name.split(".")[0].upper()
        record.name = ANSI.CYAN + f"{name.center(12):.12}" + ANSI.RESET
        record.levelname = (
            record.name
            + f" {color}["
            + f"{record.levelname.center(10):.10}"
            + f"]{ANSI.RESET} "
        )

        return super().filter(record)


def set_log_type_filter(logger_names: list[str] | str) -> None:
    logger_names = (
        logger_names if isinstance(logger_names, list) else [logger_names]
    )

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)

        in_log_type_filter = any(
            isinstance(logger_filter, LogTypeFilter)
            for logger_filter in logger.filters
        )

        if in_log_type_filter:
            continue

        logger.addFilter(LogTypeFilter())
