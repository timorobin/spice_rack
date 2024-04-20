import pytest
import datetime as dt
from pydantic import BaseModel, ValidationError, TypeAdapter
import typing as t

from spice_rack import ts_service


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


def test_tz_validator_coerce():
    class Model(BaseModel):
        est_ts: t.Annotated[
            ts_service.Timestamp,
            ts_service.validators.TzValidator(expected_tz="EST", coerce=True)
        ]

    ts_inst = ts_service.Timestamp.utcnow()
    assert ts_inst.tz == "UTC"

    model_inst = Model(est_ts=ts_inst)

    assert model_inst.est_ts.tz == "EST"


def test_tz_validator_no_coerce():
    class Model(BaseModel):
        est_ts: t.Annotated[
            ts_service.Timestamp,
            ts_service.validators.TzValidator(expected_tz="EST", coerce=False)
        ]

    ts_inst = ts_service.Timestamp.utcnow()
    assert ts_inst.tz == "UTC"

    with pytest.raises(ValidationError):
        Model(est_ts=ts_inst)
