import pytest
import datetime as dt
import zoneinfo
from pydantic import BaseModel
import json

from spice_rack import ts_service


def test_from_str():

    raw_str = "jan 5, 2022 1:15 PM EST"
    obj = ts_service.Timestamp.model_validate(raw_str)

    expected_dt_obj = dt.datetime(
        year=2022, day=5, month=1, hour=13, minute=15, tzinfo=zoneinfo.ZoneInfo("EST")
    ).astimezone(zoneinfo.ZoneInfo("UTC"))

    assert obj.to_python_timestamp() == expected_dt_obj.timestamp() * 1000 // 1000

    assert obj.to_dt_obj() == expected_dt_obj

    assert obj.to_iso_str(with_tz="EST") != obj.to_iso_str()


def test_invalid_str():
    bad_str = "???"
    with pytest.raises(ValueError):
        ts_service.Timestamp(bad_str)


def test_from_date_obj():
    date_obj = dt.date.today()
    obj = ts_service.Timestamp(date_obj)
    assert obj.to_python_timestamp() == dt.datetime.fromordinal(date_obj.toordinal()).timestamp()


def test_now():
    ts_now = ts_service.Timestamp.now()
    microsecond_now = dt.datetime.utcnow()
    millisecond_now = microsecond_now.replace(
        microsecond=microsecond_now.microsecond // 1000 * 1000
    )
    diff = millisecond_now.timestamp() - ts_now.to_python_timestamp()
    assert diff == 0


def test_ide():
    """
    Tests visually that the IDE behaves as expected.
    This can't really fail at test time like normal tests, must be evaluated visually.
    """
    # your IDE should not highlight this one bc string is ok
    assert ts_service.Timestamp("a")

    # your IDE should highlight this one bc the param doesn't have int in it, but it will
    #  validate bc we have to parse the json-encoding value
    int_ts = int(dt.datetime.now().timestamp())
    ts_service.Timestamp(int_ts)


def test_json_roundtrip():
    class X(BaseModel):
        ts: ts_service.Timestamp

    x = X(
        ts=dt.datetime.now()  # noqa -- should be coerced
    )

    json_dict = json.loads(x.json())

    x_prime = X.model_validate(json_dict)

    assert x == x_prime
    from devtools import debug
    debug(x_prime.ts.to_iso_str())
