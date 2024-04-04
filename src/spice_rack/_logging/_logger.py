from __future__ import annotations
import typing as t
import pydantic
from loguru import logger, _logger  # noqa

from spice_rack import _bases
from spice_rack._logging import _log_aug, _log_level


__all__ = (
    "Logger",
)


_ExtraLogDataT = t.Optional[list[t.Any]]
_LogLevelOrStrT = t.Union[str, _log_level.LogLevel]
LOGGER_WRAPPER_DEPTH = 4


class Logger(_bases.value_model.ValueModelBase):
    _cached_service_name: t.ClassVar[str] = "unknown"
    _logger_wrapper_depth: t.ClassVar[int] = 4
    service_name: str

    @pydantic.model_validator(mode="before", )
    def _use_cached_service_name_if_not_specified(cls, data: t.Any) -> t.Any:
        if isinstance(data, dict):
            service_name: str
            existing_service_name_maybe = data.get("service_name")
            if not existing_service_name_maybe:
                service_name = cls._cached_service_name
            else:
                service_name = existing_service_name_maybe
            data["service_name"] = service_name
        return data

    def cache_service_name(self) -> None:
        """save service name as the cached class attribute"""
        type(self)._cached_service_name = self.service_name

    @property
    def loguru_logger(self) -> _logger.Logger:
        return logger

    @staticmethod
    def _format_log_extra_data(
            extra_data: _ExtraLogDataT
    ) -> _log_aug.ExtraLogDataContainer:
        res: list[_log_aug.ExtraLogData] = []
        if extra_data:
            for data_i in extra_data:
                formatted_aug = _log_aug.ExtraLogData.parse_from_raw_data(data_i)
                res.append(formatted_aug)
        return _log_aug.ExtraLogDataContainer.model_validate(res)

    def _get_depth(self, depth_adj: t.Optional[int]) -> int:
        """gets the adjusted depth"""
        depth = self._logger_wrapper_depth
        if depth_adj:
            depth = depth + depth_adj

        if depth < 0:
            raise ValueError(
                f"depth can't be less than 0, encountered {depth}"
            )
        return depth

    def _log(
            self,
            level: _log_level.LogLevel,
            msg: str,
            extra_data: _ExtraLogDataT,
            depth: t.Optional[int] = None,
    ) -> None:
        # catch errors and logs them, without blowing
        try:
            extra_data = self._format_log_extra_data(extra_data).get_logger_repr()

        except Exception as e:
            self._log(
                level=_log_level.LogLevel.model_validate("error"),
                msg="failed to format the specified extra data",
                extra_data=[str(e)],
                # manually specify depth here to be 0 bc this is an error within this logger
                depth=-1*self._logger_wrapper_depth
            )
            return

        try:
            loguru_level: str = str(level).upper()
            loguru_logger_inst = self.loguru_logger.opt(depth=self._get_depth(depth))
            loguru_logger_inst.log(
                loguru_level, msg,
                service_name=self.service_name,
                extra_data=extra_data
            )

        except Exception as e:
            self._log(
                level=_log_level.LogLevel.model_validate("error"),
                msg="error encountered when calling the loguru logger",
                extra_data=[str(e)],

                # manually specify depth here to be 0 bc this is an error within this logger
                depth=-1*self._logger_wrapper_depth
            )
            return

    def log(
            self,
            level: _log_level.LogLevel,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ) -> None:
        return self._log(
            level=_log_level.LogLevel.model_validate(level),
            msg=msg,
            extra_data=extra_data,
            depth=depth
        )

    def debug(
            self,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ):
        self.log(
            level=_log_level.LogLevel("debug"),
            msg=msg,
            extra_data=extra_data,
            depth=depth
        )

    def info(
            self,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ):
        self.log(
            level=_log_level.LogLevel("info"),
            msg=msg,
            extra_data=extra_data,
            depth=depth
        )

    def error(
            self,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ):
        self.log(
            level=_log_level.LogLevel("error"),
            msg=msg,
            extra_data=extra_data,
            depth=depth
        )

    def critical(
            self,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ):
        self.log(
            level=_log_level.LogLevel("critical"),
            msg=msg,
            extra_data=extra_data,
            depth=depth
        )

    def exception(
            self,
            msg: str,
            extra_data: _ExtraLogDataT = None,
            depth: t.Optional[int] = None
    ):
        # catch errors and logs them, without blowing
        try:
            extra_data = self._format_log_extra_data(extra_data).get_logger_repr()

        except Exception as e:
            self._log(
                level=_log_level.LogLevel.model_validate("error"),
                msg="failed to format the specified log augmentations",
                extra_data=[str(e)],
                # manually specify depth here to be 0 bc this is an error within this logger
                depth=-1*self._logger_wrapper_depth
            )
            return

        try:
            loguru_level: str = str(_log_level.LogLevel("error")).upper()
            loguru_logger_inst = self.loguru_logger.opt(depth=self._get_depth(depth))
            loguru_logger_inst.log(
                loguru_level, msg,
                service_name=self.service_name,
                extra_data=extra_data
            )

        except Exception as e:
            self._log(
                level=_log_level.LogLevel.model_validate("error"),
                msg="error encountered when calling the loguru logger",
                extra_data=[str(e)],

                # manually specify depth here to be 0 bc this is an error within this logger
                depth=-1*self._logger_wrapper_depth
            )
            return
