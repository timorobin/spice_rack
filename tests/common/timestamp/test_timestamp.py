import pytest
import datetime as dt
import zoneinfo
from pydantic import BaseModel
import json

from spice_rack import common


def test_from_str():

    raw_str = "jan 5, 2022 1:15 PM EST"
    obj = common.timestamp.Timestamp(raw_str)

    expected_dt_obj = dt.datetime(
        year=2022, day=5, month=1, hour=13, minute=15, tzinfo=zoneinfo.ZoneInfo("EST")
    ).astimezone(zoneinfo.ZoneInfo("UTC"))

    assert obj.to_python_timestamp() == expected_dt_obj.timestamp() * 1000 // 1000

    assert obj.to_dt_obj() == expected_dt_obj

    assert obj.to_iso_str(with_tz="EST") != obj.to_iso_str()


def test_invalid_str():
    bad_str = "???"
    with pytest.raises(ValueError):
        common.timestamp.Timestamp(bad_str)


def test_from_date_obj():
    date_obj = dt.date.today()
    obj = common.timestamp.Timestamp(date_obj)
    assert obj.to_python_timestamp() == dt.datetime.fromordinal(date_obj.toordinal()).timestamp()


def test_now():
    ts_now = common.timestamp.Timestamp.now()
    microsecond_now = dt.datetime.utcnow()
    millisecond_now = microsecond_now.replace(
        microsecond=microsecond_now.microsecond // 1000 * 1000
    )
    diff = millisecond_now.timestamp() - ts_now.to_python_timestamp()
    assert diff == 0


def test_json_roundtrip():
    class X(BaseModel):
        ts: common.timestamp.Timestamp

    x = X(
        ts=dt.datetime.now()  # noqa -- should be coerced
    )

    json_dict = json.loads(x.json())

    x_prime = X.parse_obj(json_dict)

    assert x == x_prime
    from devtools import debug
    debug(x_prime.ts.to_iso_str())
