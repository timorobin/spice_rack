from __future__ import annotations
from typing import Union, Any
from typing_extensions import TypeAlias
# from http import HTTPStatus
from pydantic import Field

from spice_rack._base_classes import _pydantic


__all__ = (
    "HttpStatusCodeT",
    "HttpStatusCodeOrIntT",
    "WrappedExternalException"
)

# changed to int to allow for custom codes
HttpStatusCodeT: TypeAlias = int  # HTTPStatus
HttpStatusCodeOrIntT: TypeAlias = Union[HttpStatusCodeT, int]


class WrappedExternalException(_pydantic.AbstractValueModel):
    """a wrapper around an unknown error not one of our custom ones"""
    type: str = Field(description="the name of the type of the error")
    detail: str = Field(description="The string representation of the error")

    @classmethod
    def validate(cls, value: Any) -> WrappedExternalException:
        if isinstance(value, Exception):
            value = {
                "type": type(value).__name__,
                "detail": str(value),
            }
        res = super().validate(value)
        assert isinstance(res, WrappedExternalException), type(res)
        return res
