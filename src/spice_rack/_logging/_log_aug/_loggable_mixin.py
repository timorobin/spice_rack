from __future__ import annotations
from abc import ABC, abstractmethod
import typing as t

from spice_rack._logging._log_aug._container import ExtraLogData


__all__ = (
    "LoggableObjMixin",
)


class LoggableObjMixin(ABC):
    """
    provides interface for customizing how our logger formats a given class
    """

    # make sure this is the same as the method we specify in the container class
    @abstractmethod
    def __get_logger_data__(self) -> t.Union[str, t.Dict, ExtraLogData]:
        """
        mixin that informs which method to implement to add a hook
        that our logger will use to format how we represent this object
        in the logs.

        Returns: a dict of json-encodeable data
        """
        raise NotImplementedError()

    @t.final
    def __format_for_logger__(self) -> ExtraLogData:
        """this calls '__get_logger_data__' to get the data to log"""
        logger_data = self.__get_logger_data__()
        return ExtraLogData.parse_from_raw_data(data=logger_data)
