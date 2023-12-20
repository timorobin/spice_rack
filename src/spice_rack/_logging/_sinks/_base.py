# from __future__ import annotations
# from abc import abstractmethod
# from typing import TYPE_CHECKING
# from pydantic import Field
#
# from strlt_common.model_bases import AbstractValueModel, DispatchableModelMixin
# from strlt_logging.log_level_enum import LogLevelEnum
#
# if TYPE_CHECKING:
#     from loguru import Logger
#
#
# __all__ = (
#     "AbstractLogSink",
# )
#
#
# class AbstractLogSink(DispatchableModelMixin, AbstractValueModel):
#     level: LogLevelEnum = Field(
#         description="the level for this logger", default=LogLevelEnum.INFO
#     )
#     backtrace: bool = Field(
#         description="if true, we automatically include tracebacks"
#                     " when we are logging an error. We can still augment our "
#                     "logs with a call stack whenever we want, "
#                     "regardless of if we are in the exception context. "
#                     "see the relevant log augmentor"
#                     "see `docs <https://loguru.readthedocs.io/en/stable/overview.html"
#                     "#fully-descriptive-exceptions>`_",
#         default=True
#     )
#     diagnose: bool = Field(
#         description="if we true, we annotate the stacktrace with values of specific variables"
#                     " in the stack trace. Like as debugger. "
#                     "see `docs <https://loguru.readthedocs.io/en/stable/overview.html"
#                     "#fully-descriptive-exceptions>`_",
#         default=False
#     )
#     struct_log: bool = Field(
#         description="if true, we serialize the logs for usage in a structured way. "
#                     "this field is used when building the loguru_kwargs "
#                     "passed in when setting up the sink",
#         default=False
#     )
#     ignore_log_augmentations: bool = Field(
#         description="if true we ignore all log augmentation", default=False
#     )
#
#     @abstractmethod
#     def setup(self, logger: Logger, **loguru_kwargs) -> None:
#         raise NotImplementedError()
#
#     def __repr__(self) -> str:
#         return f"{self.class_id}[level='{self.level}']"
