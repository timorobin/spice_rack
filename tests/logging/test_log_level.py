import pytest

from spice_rack import logging


def test_schema_build():
    assert logging.LogLevel.model_json_schema()


@pytest.mark.parametrize(
    "str_log_level",
    list(logging.LogLevel._str_to_int.keys())
)
def test_all_str_vals(str_log_level: str):
    # ensure it is parsed correctly
    log_level = logging.LogLevel(str_log_level)

    # ensure we can cast to int
    assert int(log_level)

    # ensure we can cast to str correctly
    assert str(log_level) == str_log_level

    # ensure we can parse upper case too
    assert logging.LogLevel(str_log_level.upper())


@pytest.mark.parametrize(
    "int_log_level",
    list(logging.LogLevel._int_to_str.keys())
)
def test_all_int_vals(int_log_level: int):
    # ensure it is parsed correctly
    log_level = logging.LogLevel(int_log_level)

    # ensure we can cast to int
    assert int(log_level) == int_log_level

    # ensure we can cast to str correctly
    assert str(log_level)
