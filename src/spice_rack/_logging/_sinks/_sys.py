from __future__ import annotations
import typing as t
import sys
from pydantic import Field

from spice_rack._logging._sinks import _base

if t.TYPE_CHECKING:
    from loguru import Logger

__all__ = (
    "SysLogSink",
)


class SysLogSink(_base.AbstractLogSink, class_id="sys"):
    channel: t.Literal["stdout", "stderr"] = "stdout"
    struct_log: bool = Field(
        description="if true, we serialize the logs for usage in a structured way. "
                    "this field is used when building the loguru_kwargs "
                    "passed in when setting up the sink."
                    "This must be False for system-based log sink",
        default=False,
    )

    def setup(self, logger: Logger, **custom_loguru_kwargs) -> None:
        std_dest = getattr(sys, self.channel)

        loguru_kwargs = self._get_loguru_kwargs()
        loguru_kwargs.update(custom_loguru_kwargs)
        assert std_dest
        logger.add(std_dest, **loguru_kwargs)
