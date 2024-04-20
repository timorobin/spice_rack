import datetime as dt
from pydantic import BaseModel
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
