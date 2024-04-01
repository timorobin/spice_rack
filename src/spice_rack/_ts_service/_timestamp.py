from __future__ import annotations
import typing as t
import datetime as dt
import dateparser
import pydantic

from spice_rack._ts_service._tz_key import TimeZoneKey
from spice_rack import _logging


__all__ = (
    "Timestamp",
)


_TzKeyT = t.Union[str, TimeZoneKey, t.Literal["local"]]
_TimestampInitValueT = t.Union[float, str, dt.datetime, dt.date]
_PythonTimestampT = float  # seconds from epoch with decimals as sub-second measurements


class Timestamp(pydantic.RootModel[int], _logging.log_extra.LoggableObjMixin):
    """
    special subclass of 'int' that contains the utc millisecond from epoch.
    """
    _default_assumed_tz: t.ClassVar[TimeZoneKey] = TimeZoneKey("UTC")
    """timezone we assume when parsing raw data into this object"""
    # _default_tz: ClassVar[TimeZoneKey] = TimeZoneKey.local()

    def to_python_timestamp(self) -> _PythonTimestampT:
        # convert to seconds from epoch, posix timestamp
        return float(self.root) / 1000

    def to_dt_obj(
            self,
            with_tz: t.Optional[_TzKeyT] = None
    ) -> dt.datetime:
        res: dt.datetime

        if with_tz:
            utc_dt_obj = dt.datetime.fromtimestamp(
                self.to_python_timestamp(), tz=TimeZoneKey("UTC").as_zone_info()
            )
            tz_key: TimeZoneKey
            if with_tz == "local":
                tz_key = TimeZoneKey.local()
            else:
                tz_key = TimeZoneKey(str(with_tz))

            new_tz_info = tz_key.as_zone_info()
            obj_new_tz = utc_dt_obj.astimezone(tz=new_tz_info)
            res = obj_new_tz
        else:
            res = dt.datetime.fromtimestamp(
                self.to_python_timestamp(), tz=None
            )
        return res

    def to_iso_str(
            self,
            with_tz: t.Optional[_TzKeyT] = None
    ) -> str:
        """
        returns the datetime object as a formatted str

        Args:
            with_tz: a timezone key we can specify. use 'local' to use whatever timezone is local
                to the process calling this function
        Returns:
            str: formatted string
        """
        dt_obj = self.to_dt_obj(with_tz=with_tz)
        return dt_obj.isoformat()

    def to_pretty_str(
            self,
            fmat: str = "%x %X %Z",
            with_tz: t.Optional[_TzKeyT] = "local"
    ) -> str:
        """
        returns the datetime object as a formatted str, in a pretty, super readable format.
        The default is "%c %Z"

        Args:
            fmat: Optional custom formatting. See python datetime docs for formatting help.
                If not specified, we use 'auto' selected appropriate format.

            with_tz: a timezone key we can specify. use 'local' to use whatever timezone is local
                to the process calling this function
        Returns:
            str: formatted string

        Notes:
            - see the docs on format codes:
              https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        dt_obj = self.to_dt_obj(with_tz=with_tz)
        return dt_obj.strftime(fmat)

    def special_repr(self, with_tz: t.Optional[_TzKeyT] = None) -> str:
        return f"{self.__class__.__name__}['{self.to_iso_str(with_tz=with_tz)}']"

    def to_file_path_fmat(self) -> str:
        return self.to_dt_obj().strftime("%Y_%m_%dT%H_%M_%S_%f")

    @classmethod
    def _from_datetime_obj(
            cls,
            value: dt.datetime,
            assumed_tz: TimeZoneKey
    ) -> int:
        tz_info: TimeZoneKey
        if value.tzinfo:
            tz_info = TimeZoneKey(value.tzname())
        else:
            tz_info = assumed_tz

        dt_obj_utc = value.astimezone(tz_info.as_zone_info())
        return int(dt_obj_utc.timestamp() * 1000)

    @classmethod
    def _from_date_obj(
            cls,
            value: dt.date,
            assumed_tz: TimeZoneKey
    ) -> int:
        datetime_obj = dt.datetime.fromisoformat(value.isoformat())
        return cls._from_datetime_obj(datetime_obj, assumed_tz=assumed_tz)

    @classmethod
    def _from_str(
            cls,
            value: str,
            assumed_tz: TimeZoneKey
    ) -> int:
        """parse a str to datetime object then to timestamp"""
        dt_obj_maybe = dateparser.parse(value)
        if dt_obj_maybe is None:
            raise ValueError(
                f"cannot parse the string, '{value}', to a datetime object "
            )

        else:
            dt_obj: dt.datetime = dt_obj_maybe
        return cls._from_datetime_obj(value=dt_obj, assumed_tz=assumed_tz)

    @classmethod
    def _from_float(
            cls,
            value: float,
            assumed_tz: TimeZoneKey
    ) -> int:
        raise ValueError("initializing from a float is not currently supported")

    @pydantic.model_validator(mode="before")
    def _validate(cls, value: _TimestampInitValueT) -> int:
        int_data: int

        if isinstance(value, str):
            int_data = cls._from_str(value, assumed_tz=cls._default_assumed_tz)

        elif isinstance(value, dt.datetime):
            int_data = cls._from_datetime_obj(value, assumed_tz=cls._default_assumed_tz)

        elif isinstance(value, dt.date):
            int_data = cls._from_date_obj(value, assumed_tz=cls._default_assumed_tz)

        # elif isinstance(value, float):
        #     float_data = cls._from_float(value, assumed_tz=cls._default_assumed_tz)

        elif isinstance(value, (int, cls)):
            int_data = value

        else:
            raise ValueError(
                f"'{cls.__name__}' doesn't support data of type {type(value)}"
            )

        return int_data

    @classmethod
    def now(cls) -> Timestamp:
        """get now down to the millisecond, not microsecond"""
        return Timestamp(dt.datetime.utcnow())

    @classmethod
    def today(cls) -> Timestamp:
        """get the current date, as a Timestamp object."""
        dt_obj = dt.datetime.today()
        return Timestamp(dt_obj)

    def __get_logger_data__(self) -> _logging.log_extra.ExtraLogData:
        return _logging.log_extra.ExtraLogData(
            key="timestamp",
            desc="a timestamp object",
            data=self.to_iso_str()
        )
