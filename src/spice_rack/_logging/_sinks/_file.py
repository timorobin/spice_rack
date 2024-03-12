from __future__ import annotations
import typing as t
import pydantic

from spice_rack._logging._sinks._base import AbstractLogSink

if t.TYPE_CHECKING:
    from loguru import Logger


__all__ = ("FilePathLogSink",)


class FilePathLogSink(AbstractLogSink, class_id="file"):
    """
    see https://loguru.readthedocs.io/en/stable/overview.html
    #easier-file-logging-with-rotation-retention-compression
    for more info. We only support a small subset here for now
    """
    file_name_prefix: str = pydantic.Field(
        description="the prefix of the file name where we'll be writing logs"
    )
    dir_path: pydantic.DirectoryPath
    file_ext: str = "log"
    add_timestamp_to_name: bool = True
    rotation_size: t.Optional[str] = "500 MB"

    def setup(self, logger: Logger, **loguru_kwargs) -> None:
        if not self.dir_path.exists():
            self.dir_path.mkdir(parents=True, exist_ok=True)
        time_str = "{time}"
        file_name = f"{self.name}_{time_str}.{self.file_ext}"
        log_file_path = self.dir_path.joinpath(file_name)
        logger.add(
            sink=str(log_file_path),
            rotation=self.rotation_size,
            **loguru_kwargs
        )
