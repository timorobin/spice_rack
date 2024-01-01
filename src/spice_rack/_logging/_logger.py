from __future__ import annotations
from typing import Optional, Any
import logging
from loguru import logger, _logger  # noqa
import os
import warnings

from spice_rack._logging import _sinks, _log_aug, _log_level


__all__ = (
    "configure_sink_for_service",
    "configure_logging_for_python_worker",
    "configure_logging_for_uvicorn_server",
    "get_logger",
    "LoggerT"
)


def configure_sink_for_service(service_name: str, sink: _sinks.AbstractLogSink) -> None:
    if sink.struct_log is False:
        if sink.ignore_log_augmentations is True:
            add_aug_to_msg = False
        else:
            add_aug_to_msg = True
    else:
        add_aug_to_msg = False

    loguru_kwargs = {
        "level": sink.level.value.upper(),
        "format": _get_default_format(service_name=service_name, add_aug_to_msg=add_aug_to_msg),
        "serialize": sink.struct_log,
        "backtrace": sink.backtrace,
        "diagnose": sink.diagnose
    }
    try:
        sink.setup(logger=logger, **loguru_kwargs)

    # if the setup method raised a SinkSetupError on its own, we just directly raise that
    # except SinkSetupError as e:
    #     raise e

    # we convert other exceptions to SinkSetupError's
    except Exception as e:
        raise e
        # raise SinkSetupError(sink=sink, loguru_kwargs=loguru_kwargs, error=e)
    return sink.setup(logger=logger, **loguru_kwargs)


# uvicorn logging following this:
# https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/#uvicorn-only-version
def _get_default_format(service_name: Optional[str] = None, add_aug_to_msg: bool = False) -> str:
    time_section = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green>"
    level_section = "<blue>{level: <8}</>"
    service_name_section = "<magenta>{extra[service_name]: <15}</magenta>"
    line_num_section = "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    message_section = "<green>{message}</>"
    augmentations_section = "<yellow>{extra[" + "{log_augmentations_dumped}" + "]}</yellow>"

    if service_name:
        sections = [
            time_section, level_section, service_name_section, line_num_section, message_section
        ]
    else:
        sections = [
            time_section, level_section, level_section, message_section
        ]

    if add_aug_to_msg:
        sections.append(augmentations_section)

    format_str = " | ".join(sections)
    return format_str


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = get_logger().loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        get_logger().loguru_logger.opt(
            depth=depth, exception=record.exc_info
        ).log(level, record.getMessage())


SERVICE_NAME_ENV_VAR_NAME = "SERVICE_NAME"


def set_service_name_env_var(service_name: str) -> None:
    os.environ[SERVICE_NAME_ENV_VAR_NAME] = service_name


def get_service_name_from_env(default="unknown_service") -> str:
    return os.environ.get(SERVICE_NAME_ENV_VAR_NAME, default)


def configure_logging_for_uvicorn_server(
        sinks: list[_sinks.AbstractLogSink],
        service_name: str
) -> type[logger]:
    try:
        logger.remove(0)

    except ValueError as e:
        warnings.warn(str(e))

    except Exception as e:
        raise e

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]

    # changed from the tutorial
    # set to the lowest level and loguru-configured sinks will filter to their level
    logging.root.setLevel(logging.DEBUG)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    # this line was his, we configure from our setting object
    # get_logger().configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
    for sink in sinks:
        configure_sink_for_service(sink=sink, service_name=service_name)

    set_service_name_env_var(service_name=service_name)
    return get_logger(specified_service_name=service_name, persist_service_name=True)


def configure_logging_for_python_worker(
        sinks: list[_sinks.AbstractLogSink],
        service_name: str
) -> type[logger]:
    try:
        logger.remove(0)

    except ValueError as e:
        warnings.warn(str(e))

    except Exception as e:
        raise e

    for sink in sinks:
        configure_sink_for_service(sink=sink, service_name=service_name)
    set_service_name_env_var(service_name=service_name)
    return get_logger(specified_service_name=service_name, persist_service_name=True)


class _Logger:
    def __init__(self, service_name: str):
        from loguru import logger
        logger_ = logger.bind(service_name=service_name)
        logger_ = logger_.bind(**{"log_augmentations": []})
        logger_ = logger_.patch(_log_aug.log_augmentations_patcher)
        self._logger = logger_

    @property
    def loguru_logger(self) -> _logger.Logger:
        return self._logger

    @staticmethod
    def _format_log_augmentations(
            log_augmentations: Optional[list[Any]]
    ) -> list[_log_aug.GeneralLogAugmentation]:
        res: list[_log_aug.GeneralLogAugmentation] = []
        if log_augmentations:
            for raw_aug in log_augmentations:
                formatted_aug: _log_aug.GeneralLogAugmentation
                if isinstance(raw_aug, _log_aug.GeneralLogAugmentation):
                    formatted_aug = raw_aug

                else:
                    aug_kwargs: dict
                    if isinstance(raw_aug, dict):
                        if "aug_key" in raw_aug:
                            aug_kwargs = raw_aug
                        else:
                            aug_kwargs = {"data": raw_aug}
                    else:
                        aug_kwargs = {"data": raw_aug}
                    formatted_aug = _log_aug.GeneralLogAugmentation.validate(aug_kwargs)
                res.append(formatted_aug)
        return res

    def log(
            self,
            level: _log_level.LogLevel,
            msg: str,
            log_augmentations: Optional[list[Any]]
    ) -> None:
        log_augmentations = self._format_log_augmentations(log_augmentations)
        self._logger.log(
            level.value,
            msg,
            log_augmentations=log_augmentations
        )

    def debug(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        self.log(
            level=_log_level.LogLevel.DEBUG,
            msg=msg,
            log_augmentations=log_augmentations,
        )

    def info(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        self.log(
            level=_log_level.LogLevel.INFO,
            msg=msg,
            log_augmentations=log_augmentations,
        )

    def warning(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        self.log(
            level=_log_level.LogLevel.WARNING,
            msg=msg,
            log_augmentations=log_augmentations,
        )

    def error(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        self.log(
            level=_log_level.LogLevel.ERROR,
            msg=msg,
            log_augmentations=log_augmentations,
        )

    def critical(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        self.log(
            level=_log_level.LogLevel.CRITICAL,
            msg=msg,
            log_augmentations=log_augmentations,
        )

    def exception(
            self,
            msg: str,
            log_augmentations: Optional[list[Any]] = None
    ):
        log_augmentations = self._format_log_augmentations(log_augmentations)
        self.loguru_logger.exception(
            msg, log_augmentations=log_augmentations
        )


def get_logger(
        specified_service_name: Optional[str] = None,
        persist_service_name: bool = False
) -> _Logger:
    service_name: str
    if specified_service_name is None:
        service_name = get_service_name_from_env()
    else:
        service_name = specified_service_name

    if specified_service_name and persist_service_name:
        set_service_name_env_var(specified_service_name)

    return _Logger(service_name=service_name)


LoggerT = _Logger
