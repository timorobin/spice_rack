from __future__ import annotations

import typing as t
from typing import Literal, TYPE_CHECKING
import sys
from pydantic import Field

from spice_rack._logging._sinks import _base

if TYPE_CHECKING:
    from loguru import Logger

__all__ = (
    "SysLogSink",
)


class SysLogSink(_base.AbstractLogSink):
    channel: Literal["stdout", "stderr"] = "stdout"
    struct_log: bool = Field(
        description="if true, we serialize the logs for usage in a structured way. "
                    "this field is used when building the loguru_kwargs "
                    "passed in when setting up the sink."
                    "This must be False for system-based log sink",
        default=False,
    )

    @classmethod
    def get_cls_id(cls) -> t.Optional[_base.LogSinkTypeEnum]:
        return _base.LogSinkTypeEnum.SYS

    def setup(self, logger: Logger, **loguru_kwargs) -> None:
        std_dest = getattr(sys, self.channel)
        assert std_dest
        logger.add(std_dest, **loguru_kwargs)
