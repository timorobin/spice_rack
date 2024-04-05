from __future__ import annotations
import typing as t

from spice_rack._logging._logger import Logger


__all__ = (
    "get_logger",
)


def get_logger(
        specified_service_name: t.Optional[str] = None,
) -> Logger:
    """
    function that returns a logger.
    This is here for backward compatibility of the api but you should be using
    Logger.get_logger instead
    """
    return Logger.get_logger(specified_service_name)
