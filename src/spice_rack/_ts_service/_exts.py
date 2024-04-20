from __future__ import annotations
import typing as t
import pydantic
import datetime as dt

from spice_rack._ts_service import _validators, _timestamp, _tz_key
from spice_rack import _bases


__all__ = (
    "TimestampAutoParseStrT",
    "timestamp_auto_str_parse_ta",
    "UtcMicrosecondTimestamp",
    "utc_microsecond_timestamp_ta"
)


TimestampAutoParseStrT = t.Annotated[
    _timestamp.Timestamp,
    _validators.StrParser()
]
"""
this type annotation when used within the pydantic context will use dateparser to automatically
parse any strings to the Timestamp instance. This is potentially very slow so use it carefully when convenience 
and flexibility trumps everything else.

Example using as a field annotation::

    class Model(pydantic.BaseModel):
        ts: Timestamp
        ts_flexible: TimestampAutoParseStrT
    
    date_str = "Aug 13th 1995"
    Model(
        ts=date_str,  # will fail validation
        annotated_ts=date_str  # will be parsed
    )
"""


timestamp_auto_str_parse_ta: pydantic.TypeAdapter[TimestampAutoParseStrT] = pydantic.TypeAdapter(TimestampAutoParseStrT)
"""
type adapter to get the pydantic parsing behavior 'TimestampAutoParseStrT' outside the pydantic context.

Example using as standalone parser::

    class Model(pydantic.BaseModel):
        ts: Timestamp
        ts_flexible: TimestampAutoParseStrT
    
    date_str = "Aug 13th 1995"
    Timestamp.model_validate(date_str)  # will fail
    timestamp_auto_str_parse_ta.validate_python(date_str) # will parse to a Timestamp instance
"""


def _utc_us_before_val_func(__obj: t.Any) -> int:
    if isinstance(__obj, (_timestamp.Timestamp, dt.datetime, dt.date)):
        return _timestamp.Timestamp.model_validate(__obj).microseconds
    else:
        return __obj


def _utc_us_after_val_func(__obj: int) -> int:
    # todo: validate it is a valid microseconds from epoch value
    return __obj


_UsIntTypeAnn = t.Annotated[
    int,
    pydantic.BeforeValidator(_utc_us_before_val_func),
    pydantic.AfterValidator(_utc_us_after_val_func)
]


class UtcMicrosecondTimestamp(_bases.RootModel[_UsIntTypeAnn]):
    """
    wraps an integer that passes through our Timestamp class during validation to ensure it is a valid microsecond
    timestamp. This is useful when you want to represent the serialize the timestamp as an int, like in a database
    column or something similar where you don't want the complex object, and you're ok with throwing away
    the timezone information.
    """
    def to_timestamp_inst(self) -> _timestamp.Timestamp:
        return _timestamp.Timestamp(
            microseconds=self.root,
            tz=_tz_key.TimeZoneKey("UTC")
        )


utc_microsecond_timestamp_ta: pydantic.TypeAdapter[int] = pydantic.TypeAdapter(_UsIntTypeAnn)
"""
wraps an integer that passes through our Timestamp class during validation to ensure it is a valid microsecond
timestamp. This is useful when you want to represent the serialize the timestamp as an int, like in a database
column or something similar where you don't want the complex object, and you're ok with throwing away 
the timezone information.
"""
