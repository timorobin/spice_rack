from __future__ import annotations
import typing as t
import pydantic

__all__ = (
    "SpecialStrBase",
)


# coercible type annotation specifying you could also initialize this class with.
_CoercibleTV = t.TypeVar("_CoercibleTV", )
SelfTV = t.TypeVar("SelfTV", bound="SpecialStrBase")


class SpecialStrBase(pydantic.RootModel[str]):
    """container for a special string to avoid having """
    _default_equality_mode: t.Literal["strict", "lax"] = "lax"

    def __str__(self) -> str:
        return self.root

    def special_repr(self) -> str:
        """
        Gives us a special representation indicating the instance is a special string, not just
        a normal one.

        This keeps the regular '__repr__' method is the same as a normal str instance
        """
        return f"{self.__class__.__name__}['{str(self)}']"

    @classmethod
    def _parse_non_str(cls, root_data: t.Any) -> str:
        """overwrite this to allow the special str class to parse non-string input"""
        raise TypeError(f"'{cls.__name__}' cannot parse data of type {type(root_data)}")

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        """overwrite this to specify the custom str formatting for this class"""
        return root_data

    @classmethod
    def _validate_str_val(cls, root_data: str) -> str:
        """validate that the formatted string data is valid"""
        return root_data

    @pydantic.field_validator("root", mode="before")
    def _coerce_and_validate(cls: t.Type[SelfTV], v: t.Any) -> str:
        str_val: str
        if not isinstance(v, str):
            str_val = cls._parse_non_str(v)
        else:
            str_val = v

        str_val = cls._format_str_val(str_val)
        str_val = cls._validate_str_val(str_val)
        return str_val

    def __hash__(self: SelfTV) -> int:
        return hash(str(self))

    def strict_equals(self: SelfTV, other: SelfTV) -> bool:
        if not isinstance(other, type(self)):
            return False
        else:
            return str(self) == str(other)

    def lax_equals(self: SelfTV, other: t.Union[SelfTV, str]) -> bool:
        other_formatted = self.model_validate(other)
        return str(self) == str(other_formatted)

    def __eq__(self: SelfTV, other: t.Union[SelfTV, str]) -> bool:
        if self._default_equality_mode == "lax":
            return self.lax_equals(other=other)
        elif self._default_equality_mode == "strict":
            return self.strict_equals(other=other)
        else:
            raise ValueError(f"'{self._default_equality_mode}' is  not supported")
