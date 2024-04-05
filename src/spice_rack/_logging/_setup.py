from __future__ import annotations
import typing as t
import logging
from loguru import logger as loguru_logger
import warnings

from spice_rack._logging import _sinks


__all__ = (
    "configure_sink_for_service",
    "configure_logging_for_python_worker",
    "configure_logging_for_uvicorn_server",
)


def configure_sink_for_service(
        sink: _sinks.AbstractLogSink,
        custom_loguru_kwargs: t.Optional[t.Dict[str, t.Any]] = None,
) -> None:
    custom_loguru_kwargs = {} if not custom_loguru_kwargs else custom_loguru_kwargs
    try:
        sink.setup(logger=loguru_logger, **custom_loguru_kwargs)

    # if the setup method raised a SinkSetupError on its own, we just directly raise that
    # except SinkSetupError as e:
    #     raise e

    # we convert other exceptions to SinkSetupError's
    except Exception as e:
        raise e
        # raise SinkSetupError(sink=sink, loguru_kwargs=loguru_kwargs, error=e)


class _UvicornInterceptHandler(logging.Handler):
    """allows loguru to work well with uvicorn servers"""
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        from spice_rack._logging._logger_getter import get_logger
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


def configure_logging_for_uvicorn_server(
        sinks: list[_sinks.AbstractLogSink],
) -> None:
    try:
        loguru_logger.remove(0)

    except ValueError as e:
        warnings.warn(str(e))

    except Exception as e:
        raise e

    # intercept everything at the root logger
    logging.root.handlers = [_UvicornInterceptHandler()]

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
        configure_sink_for_service(sink=sink)


def configure_logging_for_python_worker(
        sinks: list[_sinks.AbstractLogSink],
) -> None:
    try:
        loguru_logger.remove(0)

    except ValueError as e:
        warnings.warn(str(e))

    except Exception as e:
        raise e

    for sink in sinks:
        configure_sink_for_service(sink=sink)
