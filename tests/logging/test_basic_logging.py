import pytest

from spice_rack import logging


@pytest.fixture(scope="module")
def sys_out_sink() -> logging.sinks.SysLogSink:
    return logging.sinks.SysLogSink(

    )
