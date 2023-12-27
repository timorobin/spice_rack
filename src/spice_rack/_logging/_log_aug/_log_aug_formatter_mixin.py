from __future__ import annotations
from abc import ABC, abstractmethod

__all__ = (
    "LogAugFormatterMixin",
)


class LogAugFormatterMixin(ABC):
    """enforces the interface for hooking in to our log augmentation formatter"""

    # make sure this is the same as the method we specify in the container class
    @abstractmethod
    def __as_log_aug__(self) -> dict:
        """
        mixin that informs which method to implement to add a hook
        that our logger will use to format how we represent this object
        in the logs.

        Returns: a dict of json-encodeable data
        """
        raise NotImplementedError()
