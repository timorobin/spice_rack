from __future__ import annotations
import typing as t
from typing_extensions import TypeAlias
import warnings

from loguru import _logger as _loguru_module  # noqa
from spice_rack import _bases
from spice_rack._logging import _log_aug, _log_level, _sinks


__all__ = (
    "Logger",
)

LoguruLoggerT: TypeAlias = _loguru_module.Logger

_ExtraLogDataT = t.Optional[list[t.Any]]
_LogLevelOrStrT = t.Union[str, _log_level.LogLevel]


class Logger(_bases.base_base.PydanticBase):
    """
    The main interface. Use the 'setup_logger' classmethod to configure the logger
    and 'get_logger' classmethod to get a Logger instance to use.
    The methods are the standard ones you'd want in a logger.
    """
    _cached_logger: t.ClassVar[t.Optional[Logger]] = None
    """previously set up logger"""

    _logger_wrapper_depth: t.ClassVar[int] = 4
    """ensures we use the part of the stack that actually called the logger"""

    _default_service_name: t.ClassVar[str] = "unknown"
    """the default service name we'll use"""

    service_name: str
    """the name of the service to use"""

    sinks: t.List[_sinks.AnySinkT]
    """
    the sink configs we used for this logger. Merely there for informational purposes as they are used for
    setup prior to initializing this instance
    """

    @classmethod
    def setup_logger(
            cls,
            service_name: str,
            sinks: t.List[_sinks.AnySinkT],
            cache_res: bool = True,
    ) -> Logger:
        """
        Sets up the logger with the sinks and the service name.
        Use this classmethod to initially set up a logger and for all subsequent calls,
        use 'get_logger' class method.

        Args:
            service_name: the name of the service we are setting up the logger for
            sinks: the sink configs we want to use
            cache_res: if True, we cache the Logger inst for later usage. default is True

        Returns:
            Logger: a setup logger inst
        """
        if sinks:
            from spice_rack._logging._setup import configure_logging_for_python_worker
            configure_logging_for_python_worker(sinks=sinks)
        logger_inst = Logger(
            service_name=service_name,
            sinks=sinks,
        )
        if cache_res:
            cls._cached_logger = logger_inst
        return logger_inst

    @classmethod
    def get_logger(cls, service_name: t.Optional[str] = None) -> Logger:
        """
        get a previously set up logger. If nothing specified, we'll create a logger with no sink configs and raise a
        warning about it.

        Args:
            service_name: if specified, we'll change the service name to this value, otherwise it'll be unchanged

        Returns: a Logger instance
        """
        logger_inst: Logger

        if cls._cached_logger is None:
            warnings.warn(
                "no logger instance found, we setup a basic logger to use. "
                "Make sure you didn't forget to configure your logger"
            )
            logger_inst = cls.setup_logger(
                service_name=service_name if service_name else cls._default_service_name,
                sinks=[],
                cache_res=True
            )
        else:
            logger_inst = cls._cached_logger

        if service_name:
            logger_inst.service_name = service_name
        return logger_inst

    def _post_init_setup(self) -> None:
        self.loguru_logger.configure(extra={"service_name": self.service_name, "extra_data": ""})

    @property
    def loguru_logger(self) -> LoguruLoggerT:
        """the underlying loguru logger instance"""
        from loguru import logger as loguru_logger
        return loguru_logger

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
