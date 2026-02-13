from enum import Enum


class ErrorLevel(str, Enum):
    """Enumeration of supported event severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TimeEnum(str, Enum):
    """Enumeration of supported time bucket intervals for statistics."""

    HOUR = "hour"
    DAY = "day"
