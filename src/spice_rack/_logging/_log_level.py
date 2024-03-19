from __future__ import annotations
import typing as t
import pydantic

from spice_rack import _bases

__all__ = (
    "LogLevel",
)


_LogLevelStrLiteralT = t.Literal[
    "debug",
    "info",
    "warning",
    "error",
    "critical"
]
_LogLevelIntLiteralT = t.Literal[
    10,
    20,
    30,
    40,
    50
]


_LogLevelLiteralT = t.Union[_LogLevelStrLiteralT, _LogLevelIntLiteralT]

_str_to_int: t.Dict[_LogLevelStrLiteralT, _LogLevelIntLiteralT] = dict(
    zip(t.get_args(_LogLevelStrLiteralT), t.get_args(_LogLevelIntLiteralT))
)
_int_to_str: t.Dict[_LogLevelIntLiteralT, _LogLevelStrLiteralT] = dict(
    zip(t.get_args(_LogLevelIntLiteralT), t.get_args(_LogLevelStrLiteralT))
)


class LogLevel(_bases.root.RootModel[_LogLevelLiteralT]):
    """
    a root model holding enum values.
    """
    _str_to_int: t.ClassVar[t.Dict[_LogLevelStrLiteralT, _LogLevelIntLiteralT]] = _str_to_int
    _int_to_str: t.ClassVar[t.Dict[_LogLevelIntLiteralT, _LogLevelStrLiteralT]] = _int_to_str

    @pydantic.model_validator(mode="before")
    def _ensure_lowercase(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            if not data.islower():
                data = data.lower()
        return data

    def __str__(self) -> _LogLevelStrLiteralT:
        str_val: _LogLevelStrLiteralT
        if isinstance(self.root, str):
            # must be this type
            str_val = t.cast(_LogLevelStrLiteralT, self.root)
        else:
            root_data: _LogLevelIntLiteralT = self.root
            if root_data not in self._int_to_str:
                raise ValueError(
                    f"{root_data} doesn't have a corresponding mapping to a str log level"
                )
            else:
                str_val = self._int_to_str[root_data]

        return str_val

    def __int__(self) -> _LogLevelIntLiteralT:
        int_val: _LogLevelIntLiteralT
        if isinstance(self.root, int):
            # must be one of the int literal options
            int_val = t.cast(_LogLevelIntLiteralT, self.root)

        else:
            root_data: _LogLevelStrLiteralT = self.root
            if root_data not in self._str_to_int:
                raise ValueError(
                    f"'{root_data}' doesn't have a corresponding mapping to a int log level"
                )
            else:
                int_val = self._str_to_int[root_data]

        return int_val
