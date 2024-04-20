from __future__ import annotations
import typing as t
import dateparser
import datetime as dt

import pydantic
import pydantic_core
from spice_rack import _bases
from spice_rack._ts_service._tz_key import TimeZoneKey
from spice_rack._ts_service._timestamp import Timestamp

__all__ = (
    "StrParserException",
    "StrParser",
    "StrParserStrict",
    "TzValidator"
)


class _StrParserErrorInfo(_bases.exceptions.ErrorInfoBase):
    raw_str: str = pydantic.Field(description="the string we failed to parse into date format")
    strict: bool = pydantic.Field(description="if true, this failed strict mode parsing")
    specified_date_formats: t.List[str] = pydantic.Field(description="the date formats specified ")


class StrParserException(_bases.exceptions.CustomExceptionBase[_StrParserErrorInfo]):
    def __init__(self, raw_str: str, strict: bool, specified_date_formats: t.List[str]):
        error_info = {
            "raw_str": raw_str,
            "strict": strict,
            "specified_date_formats": specified_date_formats
        }

        if strict:
            detail = f"the strict string parser failed to parse '{raw_str}'"
        else:
            detail = f"the flexible string parser failed to parse '{raw_str}'"
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=True,
            extra_info=None
        )


class StrParser:
    """
    flexible string parser using dateparser library under the hood. If you provide date_formats it will be as
    fast as a strict parser, but fallback to the slower approach if needed. Differs from StrParserStrict which will
    raise an error not fallback.

    Use this create an annotated Timestamp type within the pydantic validation framework.

    Examples:
        1. Annotate the type to parse the format::

            class Model(pydantic.BaseModel):
                ts: Timestamp
                ts_flexible: t.Annotated[Timestamp, StrParser(date_formats="%m/%d/%Y")]

            date_str = "08/13/1995"
            Model(
                ts=date_str,  # will fail validation
                annotated_ts=date_str  # will be parsed
            )

        2. StrParserStrict will not use dateparser library as a fallback::

            class Model(pydantic.BaseModel):
                ts_strict: t.Annotated[Timestamp, StrictStrParser(date_formats="%m/%d/%Y")]
                ts_flexible: t.Annotated[Timestamp, StrParser(date_formats="%m/%d/%Y")]

            date_str = "08/13/1995"
            Model(
                ts_strict=date_str_good,  # will be parsed
                ts_flexible=date_str  # will be parsed
            )

            date_str = "Aug 13th 1995"
            Model(
                ts_strict=date_str_good,  # will fail validation
                ts_flexible=date_str  # will be parsed
            )
    """
    date_formats: t.List[str]
    """specify these to indicate that the str parser should try these date formats first"""

    def __init__(self, date_formats: t.Optional[t.List[str]] = None):
        self.date_formats = date_formats if date_formats else []

    def _get_func(self) -> t.Callable[[t.Any, ], t.Any]:
        def func(data: t.Any) -> t.Any:
            if isinstance(data, str):
                parsed_maybe = dateparser.parse(data, date_formats=self.date_formats, )
                if parsed_maybe is None:
                    raise StrParserException(
                        raw_str=data,
                        specified_date_formats=self.date_formats,
                        strict=False
                    ).as_pydantic_error()
                else:
                    data = parsed_maybe
            return data
        return func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_before_validator_function(
            function=val_func,
            schema=schema
        )
        return schema


class StrParserStrict:
    """
    This will try the different string formats in order, and choose the first one that works.

    Examples:
        1. Annotate the type to parse the format::

            class Model(pydantic.BaseModel):
                ts: Timestamp
                ts_flexible: t.Annotated[Timestamp, StrParser(date_formats="%m/%d/%Y")]

            date_str = "08/13/1995"
            Model(
                ts=date_str,  # will fail validation
                annotated_ts=date_str  # will be parsed
            )

        2. StrParserStrict will not use dateparser library as a fallback::

            class Model(pydantic.BaseModel):
                ts_strict: t.Annotated[Timestamp, StrictStrParser(date_formats="%m/%d/%Y")]
                ts_flexible: t.Annotated[Timestamp, StrParser(date_formats="%m/%d/%Y")]

            date_str = "08/13/1995"
            Model(
                ts_strict=date_str_good,  # will be parsed
                ts_flexible=date_str  # will be parsed
            )

            date_str = "Aug 13th 1995"
            Model(
                ts_strict=date_str_good,  # will fail validation
                ts_flexible=date_str  # will be parsed
            )
    """
    date_formats: t.List[str]
    """specify these to indicate that the str parser should try these date formats first"""

    def __init__(self, date_formats: t.List[str]):
        if len(date_formats) == 0:
            raise ValueError(
                "You must specify at least one date_format for the StrParserStrict validator"
            )
        self.date_formats = date_formats

    def _get_func(self) -> t.Callable[[t.Any, ], t.Any]:
        def func(data: t.Any) -> t.Any:
            if isinstance(data, str):
                parsed_maybe: t.Optional[dt.datetime] = None
                for format_i in self.date_formats:
                    try:
                        parsed_maybe = dt.datetime.strptime(data, format_i)
                    except ValueError:
                        continue
                    except Exception as e:
                        raise e
                if parsed_maybe is None:
                    raise StrParserException(
                        raw_str=data,
                        specified_date_formats=self.date_formats,
                        strict=True
                    ).as_pydantic_error()
                else:
                    data = parsed_maybe
            return data
        return func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_before_validator_function(
            function=val_func,
            schema=schema
        )
        return schema


class TzValidator:
    """use as an AfterValidator to ensure the timezone is what is expected"""
    def __init__(self, expected_tz: t.Union[str, TimeZoneKey], coerce: bool = True):
        self.expected_tz = TimeZoneKey(expected_tz)
        self.coerce = coerce

    def _get_func(self) -> t.Callable[[t.Any, ], t.Any]:
        def func(ts_inst: Timestamp) -> Timestamp:
            if ts_inst.tz != self.expected_tz:
                if self.coerce:
                    ts_inst = ts_inst.with_tz(self.expected_tz)
                else:
                    raise ValueError(
                        f"expected '{self.expected_tz}' timezone, encountered '{ts_inst.tz}'"
                    )
            return ts_inst
        return func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema
