from __future__ import annotations
import typing as t
import zoneinfo
import tzlocal

from spice_rack import _bases


__all__ = (
    "TimeZoneKey",
    "InvalidTimeZoneKeyException"
)


_TZ_CHOICES_SET: t.Set[str] = zoneinfo.available_timezones()
_TZ_CHOICES_LIST: t.List[str] = list(_TZ_CHOICES_SET)


class TimeZoneKey(_bases.special_str.SpecialStrBase):
    """
    a special string representing a timezone.

    see python docs for "zoneinfo" for options:
        https://docs.python.org/3/library/zoneinfo.html
    """

    @classmethod
    def timezone_choices(cls) -> t.Set[str]:
        return _TZ_CHOICES_SET

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        # ensure it is a valid zone info
        if root_data not in cls.timezone_choices():
            raise InvalidTimeZoneKeyException(
                invalid_value=root_data,
                options=_TZ_CHOICES_LIST
            )

        else:
            return root_data

    def as_py_zone_info(self) -> zoneinfo.ZoneInfo:
        """get the timezone info in the format python datetime library uses"""
        return zoneinfo.ZoneInfo(str(self))

    @classmethod
    def local(cls) -> TimeZoneKey:
        """gets timezone info for where this process is running"""
        return _LOCAL_TZ_KEY


# set this once on import bc it is pretty slow
_LOCAL_TZ_KEY = TimeZoneKey(tzlocal.get_localzone().key)


class _InvalidTimeZoneKeyErrorInfo(_bases.exceptions.ErrorInfoBase):
    invalid_value: str
    options: list[str]


class InvalidTimeZoneKeyException(_bases.exceptions.CustomExceptionBase[_InvalidTimeZoneKeyErrorInfo]):
    def __init__(
            self,
            invalid_value: str,
            options: list[str],
            extra_info: t.Optional[dict] = None,
            verbose: bool = False
    ):
        error_info = {
            "invalid_value": invalid_value,
            "options": options
        }

        detail = f"'{invalid_value}' is not a valid timezone key."
        super().__init__(
            detail=detail,
            error_info=error_info,
            extra_info=extra_info,
            verbose=verbose
        )
