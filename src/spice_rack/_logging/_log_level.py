from __future__ import annotations

from spice_rack import _base_classes


__all__ = (
    "LogLevel",
)


class LogLevel(_base_classes.enums.StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
