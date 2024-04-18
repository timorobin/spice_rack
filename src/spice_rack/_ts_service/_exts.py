from __future__ import annotations
import typing as t
import pydantic

from spice_rack._ts_service import _validators, _timestamp


__all__ = (
    "TimestampAutoParseStrT",
    "timestamp_auto_str_parse_ta"
)


TimestampAutoParseStrT = t.Annotated[
    _timestamp.Timestamp,
    _validators.StrParser()
]
"""
this type annotation when used within the pydantic context will use dateparser to automatically
parse any strings to the Timestamp instance. This is potentially very slow so use it carefully when convenience 
and flexibility trumps everything else.
"""


timestamp_auto_str_parse_ta: pydantic.TypeAdapter[TimestampAutoParseStrT] = pydantic.TypeAdapter(TimestampAutoParseStrT)
"""
type adapter to get the pydantic parsing behavior 'TimestampAutoParseStrT' outside the pydantic context
"""

