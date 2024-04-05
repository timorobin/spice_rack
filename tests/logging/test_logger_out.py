import pytest

from spice_rack import logging


@pytest.fixture(scope="module", autouse=True)
def logger_inst() -> None:
    sinks = [
        logging.sinks.SysLogSink()
    ]
    logging.Logger.setup_logger(
        service_name="test", sinks=sinks
    )


@pytest.fixture(scope="function")
def record_checker(caplog):
    def func(
            record_ix: int = 0,
            **expected_vals
    ):
        record = caplog.records[record_ix]
        for k, v in expected_vals.items():
            record_v = getattr(record, k)
            assert record_v == v
    return func


def test_simple(record_checker):
    logger_inst = logging.Logger.get_logger()
    logger_inst.info("a info message")
    record_checker(
        msg="a info message",
        filename="python.py"  # python.py is the pytest runner
    )


def test_depth(record_checker):
    logger_inst = logging.Logger.get_logger()
    logger_inst.info("a info message", depth=-4)
    record_checker(
        msg="a info message",
        filename="_logger.py"  # the _logger.py file in spice_rack
    )


def test_extra_data(record_checker):
    logger_inst = logging.Logger.get_logger()
    logger_inst.info("a info message", extra_data=[{"k": "v"}])

    extra_data = logger_inst._format_log_extra_data([{"k": "v"}]).get_logger_repr()

    record_checker(
        msg="a info message",
        extra={"extra_data": extra_data, "service_name": "test"}
    )
