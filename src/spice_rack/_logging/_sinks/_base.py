from __future__ import annotations
import typing as t
from abc import abstractmethod
from pydantic import Field
from spice_rack import _bases
from spice_rack._logging._log_level import LogLevel

if t.TYPE_CHECKING:
    from loguru import Logger


__all__ = (
    "AbstractLogSink",
)


class AbstractLogSink(
    _bases.dispatchable.DispatchableValueModelBase,
):
    level: LogLevel = Field(
        description="the level for this logger", default=LogLevel("info")
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
    include_extra_data: bool = Field(
        description="if false, we do not include extra data for this sink", default=True
    )
    custom_loguru_fmat: t.Optional[str] = Field(
        description="an optional field you can use to manually specify the loguru format for this "
                    "sink",
        default=None
    )

    def special_repr(self) -> str:
        """get a pretty str showing simple info about this logger"""
        return f"LoggerSink[type={self.class_id}]"

    def _get_default_loguru_format(self) -> str:
        """
        the loguru fmat to use for the logger. see: loguru docs on this.
        you can also overwrite this method to customize how a specific sink builds
        their default format str

        Returns:
            str: a loguru format
        """
        time_section = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green>"
        level_section = "<blue>{level: <8}</>"
        service_name_section = "<magenta>{extra[service_name]: <15}</magenta>"
        line_num_section = "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        message_section = "<green>{message}</>"
        extra_data_section = "<yellow>extra data: {extra[" + "extra_data" + "]}</yellow>"

        sections = [
            time_section, level_section, service_name_section, line_num_section,
            message_section
        ]

        if self.include_extra_data:
            sections.append(extra_data_section)

        format_str = " | ".join(sections)
        return format_str

    def get_loguru_format(self) -> str:
        if self.custom_loguru_fmat is not None:
            return self.custom_loguru_fmat
        else:
            return self._get_default_loguru_format()

    def _get_loguru_kwargs(self) -> dict:
        """build a dict of loguru setup kwargs from this sink"""
        return {
            "level": str(self.level).upper(),
            "format": self.get_loguru_format(),
            "serialize": self.struct_log,
            "backtrace": self.backtrace,
            "diagnose": self.diagnose
        }

    @abstractmethod
    def setup(self, logger: Logger, **custom_loguru_kwargs) -> None:
        raise NotImplementedError()
