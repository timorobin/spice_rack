import pytest

from spice_rack import logging


@pytest.fixture(scope="module")
def sys_out_sink() -> logging.sinks.SysLogSink:
    return logging.sinks.SysLogSink()


def test_sys_out(sys_out_sink):
    logging.configure_logging_for_python_worker(service_name="test", sinks=[sys_out_sink])
    logger = logging.get_logger()
    logger.info("aaaa")

    logger.info("aaa", extra_data=[{"a": 1}])
    # raise ValueError("ZZZ")
