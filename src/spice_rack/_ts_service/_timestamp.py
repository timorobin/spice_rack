from __future__ import annotations
import typing as t
import datetime as dt
import pydantic
from functools import total_ordering
import zoneinfo

from spice_rack import _logging, _bases
from spice_rack._ts_service._tz_key import TimeZoneKey


__all__ = (
    "Timestamp",
)

_TzKeyT = t.Union[str, TimeZoneKey, t.Literal["local"]]
_PythonTimestampT = float  # seconds from epoch with decimals as sub-second measurements


TimestampSelfTV = t.TypeVar("TimestampSelfTV", bound="Timestamp")


@total_ordering
class Timestamp(_bases.ValueModelBase, _logging.log_extra.LoggableObjMixin):
    """
    This class represents timestamp, with microsecond precision, and the timezone info related to this timestamp
    and encapsulates common timestamp operations

    This class will automatically validate dt.datetime, dt.date and iso formatted strings. See extensions for
    more flexible parsing logic.
    """
    microseconds: int = pydantic.Field(
        description="microseconds from epoch, standardized so the timezone does not impact this value"
    )
    tz: TimeZoneKey = pydantic.Field(
        description="the timezone info for this timestamp, default is UTC",
    )

    @property
    def seconds(self) -> float:
        return self.microseconds / 1e6

    def to_python_timestamp(self) -> _PythonTimestampT:
        # convert to seconds from epoch, posix timestamp
        return float(self.microseconds) / 1e6

    def with_tz(self, __new_tz: t.Union[str, TimeZoneKey]) -> "Timestamp":
        """convert this Timestamp instance to one with the different timezone"""
        return Timestamp(
            microseconds=self.microseconds,
            tz=TimeZoneKey(str(__new_tz))
        )

    def as_utc(self) -> Timestamp:
        """convenience create a Timestamp instance in UTC timezone"""
        return self.with_tz(TimeZoneKey("UTC"))

    def to_dt_obj(
            self,
            tz_aware: bool = True
    ) -> dt.datetime:
        """
        create a python stdlib datetime object from this Timestamp,

        Args:
            tz_aware: if True, we'll create a tz aware datetime object, which means it has the tz info.
                default is True.

        Notes:
            Even if we specify tz_aware=False, the resulting python datetime object will be localized to the tz info
            on this Timestamp instance.
            See the warning here for why you probably want it this way:
                https://docs.python.org/3.9/library/datetime.html#datetime.datetime.utctimetuple
        """
        res: dt.datetime
        if tz_aware:
            utc_dt_obj = dt.datetime.fromtimestamp(
                self.to_python_timestamp(), tz=TimeZoneKey("UTC").as_py_zone_info()
            )

            if self.tz != TimeZoneKey("UTC"):
                res = utc_dt_obj.astimezone(self.tz.as_py_zone_info())
            else:
                res = utc_dt_obj
        else:
            res = dt.datetime.fromtimestamp(
                self.to_python_timestamp(), tz=None
            )
        return res

    def to_iso_str(
            self,
            tz_aware: bool = True
    ) -> str:
        """
        returns the iso formatted str, via the datetime method.
        see: https://docs.python.org/3.9/library/datetime.html#datetime.datetime.isoformat

        Args:
            tz_aware: if True, the string will contain the utc offset.

        Returns:
            str: formatted string
        """
        dt_obj = self.to_dt_obj(tz_aware=tz_aware)
        return dt_obj.isoformat()

    def to_str(
            self,
            fmat: str = "%x %X %Z",
    ) -> str:
        """
        create a string using the specified python format. see python docs for help with the codes:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

        Args:
            fmat: the python format, default is a human-readable format: "%x %X %Z"

        Returns: a formatted str
        """
        return self.to_dt_obj().strftime(fmat)

    def to_file_path_fmat(self) -> str:
        """
        convenience method to format the timestamp as a filepath friendly string, "%Y_%m_%dY%H_%M_%S_%f"
        """
        return self.to_str("%Y_%m_%dY%H_%M_%S_%f")

    def special_repr(self) -> str:
        return f"{self.__class__.__name__}['{self.to_str()}']"

    @classmethod
    def _from_datetime_datetime(
            cls,
            __obj: dt.datetime,
    ) -> Timestamp:
        """
        build the Timestamp instance from the python datetime object. If timezone specified, we'll use it otherwise
        we'll assume local as is the standard behavior
        """
        tz_key: TimeZoneKey
        if __obj.tzinfo:
            obj_tz_info: dt.tzinfo = __obj.tzinfo

            # zone info implementation vs other, pops up with
            #   the EST vs EDT (Eastern Standard Time, Eastern Daylight Savings Time).
            #  TODO: revisit this
            if isinstance(obj_tz_info, zoneinfo.ZoneInfo):
                tz_key = TimeZoneKey(obj_tz_info.key)
            else:
                tz_key = TimeZoneKey(obj_tz_info.tzname(__obj))
        else:
            tz_key = TimeZoneKey.local()
        return Timestamp(
            microseconds=int(__obj.timestamp() * 1e6),
            tz=tz_key
        )

    @classmethod
    def _from_datetime_date(
            cls,
            __obj: dt.date,
    ) -> Timestamp:
        datetime_obj = dt.datetime(year=__obj.year, month=__obj.month, day=__obj.day)
        return cls._from_datetime_datetime(datetime_obj)

    @classmethod
    def from_datetime(cls, __obj: t.Union[dt.datetime, dt.date]) -> Timestamp:
        """parse a stdlib representation of the date"""
        if isinstance(__obj, dt.datetime):
            return cls._from_datetime_datetime(__obj)
        elif isinstance(__obj, dt.date):
            return cls._from_datetime_date(__obj)
        else:
            raise ValueError(
                f"'{type(__obj)}' not one of the standard lib datetime types we support parsing"
            )

    @pydantic.model_validator(mode="before")
    @classmethod
    def _parse_common(cls, data: t.Any) -> t.Any:
        if isinstance(data, (dt.datetime, dt.date)):
            data = cls.from_datetime(data).model_dump()

        if isinstance(data, str):
            try:
                dt_obj = dt.datetime.fromisoformat(data)

            except Exception as e:
                raise ValueError(
                    f"failed to parse the string, '{data}', as iso formatted date str."
                ) from e

            data = cls.from_datetime(dt_obj).model_dump()
        return data

    @classmethod
    def now(
            cls,
            unit: t.Literal["us", "ms", "s"] = "ms",
            tz_key: t.Optional[t.Union[str, TimeZoneKey]] = None
    ) -> Timestamp:
        """
        get current date and time with local timezone, down to the specified unit

        Args:
            unit: the smallest unit to go down to.
                us: microsecond, 1 second = 1_000_000 microseconds
                ms: millisecond, 1 second = 1_000 milliseconds
                s: second, 1 second = 1 second
            tz_key: which timezone to use, if not specified, we'll use local

        Returns:
            a Timestamp instance
        """
        microseconds = int(1e6 * dt.datetime.utcnow().timestamp())

        data: int
        if unit == "us":
            data = microseconds
        elif unit == "ms":
            data = int((microseconds // 1e3) * 1e3)
        elif unit == "s":
            data = int((microseconds // 1e6) * 1e6)
        else:
            raise ValueError(f"'{unit}' is not a supported value")

        tz: TimeZoneKey
        if tz_key is not None:
            tz = TimeZoneKey(tz_key)
        else:
            tz = TimeZoneKey.local()

        return Timestamp(
            microseconds=data, tz=tz
        )

    @classmethod
    def utcnow(cls, unit: t.Literal["us", "ms", "s"] = "ms") -> Timestamp:
        """
        get current date and time with utc timezone, down to the specified unit

        Args:
            unit: the smallest unit to go down to.
                us: microsecond, 1 second = 1_000_000 microseconds
                ms: millisecond, 1 second = 1_000 milliseconds
                s: second, 1 second = 1 second

        Returns:
            a Timestamp instance
        """
        return cls.now(unit=unit, tz_key="UTC")

    @classmethod
    def today(cls) -> Timestamp:
        """get the current date, as a Timestamp object."""
        return Timestamp.model_validate(dt.datetime.today())

    def __get_logger_data__(self) -> _logging.log_extra.ExtraLogData:
        return _logging.log_extra.ExtraLogData(
            key="timestamp",
            desc="a timestamp object",
            data=self.special_repr()
        )

    def __eq__(self, other: t.Union[dt.datetime, dt.date, Timestamp]) -> bool:
        other_ts = Timestamp.model_validate(other)
        return self.microseconds == other_ts.microseconds

    def __gt__(self, other: t.Union[dt.datetime, dt.date, Timestamp]) -> bool:
        other_ts = Timestamp.model_validate(other)
        return self.microseconds > other_ts.microseconds
