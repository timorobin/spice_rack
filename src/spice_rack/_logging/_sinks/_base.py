from __future__ import annotations
import typing as t
from abc import abstractmethod
from typing import TYPE_CHECKING
from pydantic import Field
from spice_rack import _base_classes
from spice_rack._logging._log_level import LogLevel

if TYPE_CHECKING:
    from loguru import Logger


__all__ = (
    "AbstractLogSink",
)


class LogSinkTypeEnum(_base_classes.pydantic.dispatchable.ConcreteClassIdEnumBase):
    SYS = "sys"
    FILE_SINK = "file_sink"


class AbstractLogSink(
    _base_classes.pydantic.dispatchable.DispatchableModelMixin[LogSinkTypeEnum],
    _base_classes.pydantic.AbstractValueModel,
    is_new_root=True
):
    level: LogLevel = Field(
        description="the level for this logger", default=LogLevel.INFO
    )
    backtrace: bool = Field(
        description="if true, we automatically include tracebacks"
                    " when we are logging an error. We can still augment our "
                    "logs with a call stack whenever we want, "
                    "regardless of if we are in the exception context. "
                    "see the relevant log augmentor"
                    "see `docs <https://loguru.readthedocs.io/en/stable/overview.html"
                    "#fully-descriptive-exceptions>`_",
        default=True
    )
    diagnose: bool = Field(
        description="if we true, we annotate the stacktrace with values of specific variables"
                    " in the stack trace. Like as debugger. "
                    "see `docs <https://loguru.readthedocs.io/en/stable/overview.html"
                    "#fully-descriptive-exceptions>`_",
        default=False
    )
    struct_log: bool = Field(
        description="if true, we serialize the logs for usage in a structured way. "
                    "this field is used when building the loguru_kwargs "
                    "passed in when setting up the sink",
        default=False
    )
    ignore_log_augmentations: bool = Field(
        description="if true we ignore all log augmentation", default=False
    )

    @abstractmethod
    def setup(self, logger: Logger, **loguru_kwargs) -> None:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.class_id}[level='{self.level.value}']"

    @classmethod
    @abstractmethod
    def get_cls_id(cls) -> t.Optional[LogSinkTypeEnum]:
        return None
