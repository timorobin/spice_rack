from __future__ import annotations
import typing as t

from spice_rack._logging._logger import Logger


__all__ = (
    "get_logger",
)


def get_logger(
        specified_service_name: t.Optional[str] = None,
        persist_service_name: bool = False
) -> Logger:
    logger_inst = Logger(service_name=specified_service_name)
    if persist_service_name:
        logger_inst.cache_service_name()
    return logger_inst
