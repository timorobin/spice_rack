import pytest
import warnings

from ._config import TestConfig


@pytest.fixture(scope="session")
def session_config() -> TestConfig:
    return TestConfig.load()


@pytest.fixture(scope="session", autouse=True)
def configure_logger() -> None:
    """tries to configure the logger and doesn't blow up if it fails bc logging isn't tested yet at this point"""
    try:
        from spice_rack import logging
        logging.Logger.setup_logger(
            service_name="unit_tests",
            sinks=[
                logging.sinks.SysLogSink(level=logging.LogLevel("debug"))
            ]
        )
    except Exception as e:
        warnings.warn(f"logger failed setup. error: {e}")
        return

