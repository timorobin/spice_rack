import pytest
import datetime as dt
from pydantic import BaseModel, ValidationError, TypeAdapter
import typing as t
import json

from spice_rack import ts_service


def test_from_date_obj():
    date_obj = dt.date.today()
    obj = ts_service.Timestamp.model_validate(date_obj)
    assert obj.to_python_timestamp() == dt.datetime.fromordinal(date_obj.toordinal()).timestamp()


def test_now_units():
    ts_now_us = ts_service.Timestamp.now("us")
    ts_now_ms = ts_service.Timestamp.now("ms")
    ts_now_s = ts_service.Timestamp.now("s")

    assert ts_now_us.microseconds > ts_now_ms.microseconds > ts_now_s.microseconds

    assert str(ts_now_ms.microseconds).endswith("000")

    assert str(ts_now_s.microseconds).endswith("000000")


def test_now():
    ts_now = ts_service.Timestamp.now(unit="ms")
    microsecond_now = dt.datetime.utcnow()
    millisecond_now = microsecond_now.replace(
        microsecond=microsecond_now.microsecond // 1000 * 1000
    )
    diff = millisecond_now.timestamp() - ts_now.to_python_timestamp()
    assert diff == 0


def test_json_roundtrip():
    class X(BaseModel):
        ts: ts_service.Timestamp

    x = X(
        ts=dt.datetime.now()  # noqa -- should be coerced
    )

    json_dict = json.loads(x.model_dump_json())

    x_prime = X.model_validate(json_dict)

    assert x == x_prime
    from devtools import debug
    debug(x_prime.ts.to_iso_str())


@pytest.fixture(scope="module")
def str_parser_info() -> t.Tuple[str, str, str]:
    date_format = "%m/%d/%Y"
    nice_str = "08/13/1995"
    messy_str = "jan 5, 2022 1:15 PM EST"

    assert dt.datetime.strptime(nice_str, date_format)

    return date_format, nice_str, messy_str


def test_timestamp_str_parse_raises(str_parser_info):
    date_format, nice_str, messy_str = str_parser_info

    # regular Timestamp can't parse either of them
    with pytest.raises(ValidationError):
        ts_service.Timestamp.model_validate(nice_str)

    with pytest.raises(ValidationError):
        ts_service.Timestamp.model_validate(messy_str)


def test_from_str_strict(str_parser_info):
    date_format, nice_str, messy_str = str_parser_info

    ta = TypeAdapter(
        t.Annotated[
            ts_service.Timestamp,
            ts_service.validators.StrParserStrict(
                date_formats=[date_format]
            )
        ]
    )

    # nice parses but messy doesn't
    ts_obj = ta.validate_python(nice_str)
    assert isinstance(ts_obj, ts_service.Timestamp)

    with pytest.raises(ValidationError):
        ta.validate_python(messy_str)


def test_from_str_flexible(str_parser_info):
    date_format, nice_str, messy_str = str_parser_info

    ta = TypeAdapter(
        t.Annotated[
            ts_service.Timestamp,
            ts_service.validators.StrParser(
                date_formats=[date_format]
            )
        ]
    )

    # nice and messy parse
    ts_obj = ta.validate_python(nice_str)
    assert isinstance(ts_obj, ts_service.Timestamp)

    ts_obj = ta.validate_python(messy_str)
    assert isinstance(ts_obj, ts_service.Timestamp)

    # crazy one doesn't
    with pytest.raises(ValidationError):
        ta.validate_python("???")
