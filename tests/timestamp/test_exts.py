import pytest
import datetime as dt
from pydantic import BaseModel, ValidationError
import typing as t

from spice_rack import ts_service


@pytest.fixture(scope="module")
def str_parser_info() -> t.Tuple[str, str, str]:
    date_format = "%m/%d/%Y"
    nice_str = "08/13/1995"
    messy_str = "jan 5, 2022 1:15 PM EST"

    assert dt.datetime.strptime(nice_str, date_format)

    return date_format, nice_str, messy_str


def test_from_str_auto_parse(str_parser_info):
    date_format, nice_str, messy_str = str_parser_info

    class Model(BaseModel):
        ts: ts_service.exts.TimestampAutoParseStrT

    # nice and messy parse
    inst = Model(ts=nice_str)
    assert isinstance(inst.ts, ts_service.Timestamp)

    ts_obj = ts_service.exts.timestamp_auto_str_parse_ta.validate_python(messy_str)
    assert isinstance(ts_obj, ts_service.Timestamp)

    # crazy one doesn't
    with pytest.raises(ValidationError):
        ts_service.exts.timestamp_auto_str_parse_ta.validate_python("???")


def test_int_container():
    ts_inst = ts_service.Timestamp.now()
    dt_inst = ts_inst.to_dt_obj()
    us_raw = ts_inst.microseconds

    class Model(BaseModel):
        ts: ts_service.exts.UtcMicrosecondTimestamp

    for ts_repr in [ts_inst, dt_inst, us_raw]:
        model_inst = Model.model_validate(
            {"ts": ts_repr}
        )
        assert model_inst.ts.root == us_raw
        assert model_inst.model_dump(mode="json")["ts"] == us_raw
        assert model_inst.ts.to_timestamp_inst() == ts_inst
        assert model_inst.model_validate_json(model_inst.model_dump_json())
