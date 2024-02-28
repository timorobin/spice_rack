from __future__ import annotations
from abc import ABC, abstractmethod

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
    def format_for_logger(self) -> ExtraLogData:
        """
        mixin that informs which method to implement to add a hook
        that our logger will use to format how we represent this object
        in the logs.

        Returns: a dict of json-encodeable data
        """
        raise NotImplementedError()
