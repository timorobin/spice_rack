from __future__ import annotations
from typing import Optional
import zoneinfo
import tzlocal

from spice_rack import _bases


__all__ = (
    "TimeZoneKey",
    "InvalidTimeZoneKeyException"
)


# todo: specify these or find another way
class TimeZoneKey(_bases.special_str.SpecialStrBase):
    """
    a special string representing a timezone.

    see python docs for "zoneinfo" for options:
        https://docs.python.org/3/library/zoneinfo.html
    """

    @classmethod
    def timezone_choices(cls) -> list[str]:
        return list(zoneinfo.available_timezones())

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        # ensure it is a valid zone info
        choices = zoneinfo.available_timezones()
        if root_data not in choices:
            raise InvalidTimeZoneKeyException(
                invalid_value=root_data,
                options=list(choices)
            )

        else:
            return root_data

    def as_zone_info(self) -> zoneinfo.ZoneInfo:
        return zoneinfo.ZoneInfo(str(self))

    @classmethod
    def local(cls) -> TimeZoneKey:
        """gets timezone info for where this process is running"""
        return TimeZoneKey(tzlocal.get_localzone().key)


# class _InvalidTimeZoneKeyErrorInfo(exception_base.ErrorInfoBase):
#     invalid_value: str
#     options: list[str]
#
#
# class InvalidTimeZoneKeyException(exception_base.ExceptionBase[_InvalidTimeZoneKeyErrorInfo]):
#     def __init__(
#             self,
#             invalid_value: str,
#             options: list[str],
#             extra_info: Optional[dict] = None,
#             verbose: bool = False
#     ):
#         error_info = {
#             "invalid_value": invalid_value,
#             "options": options
#         }
#
#         detail = f"'{invalid_value}' is not a valid timezone key."
#         super().__init__(
#             detail=detail,
#             error_info=error_info,
#             extra_info=extra_info,
#             verbose=verbose
#         )


# for now
class InvalidTimeZoneKeyException(Exception):
    def __init__(
            self,
            invalid_value: str,
            options: list[str],
            extra_info: Optional[dict] = None,
            verbose: bool = False
    ):
        # error_info = {
        #     "invalid_value": invalid_value,
        #     "options": options
        # }
        detail = f"'{invalid_value}' is not a valid timezone key."
        # super().__init__(
        #     detail=detail,
        #     error_info=error_info,
        #     extra_info=extra_info,
        #     verbose=verbose
        # )
        super().__init__(detail)
