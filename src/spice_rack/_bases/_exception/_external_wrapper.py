from __future__ import annotations
import typing as t
# from http import HTTPStatus
import pydantic

from spice_rack._bases._value_model import ValueModelBase


__all__ = (
    "WrappedExternalException",
)


class WrappedExternalException(ValueModelBase):
    type: str = pydantic.Field(description="the name of the type of the error")
    detail: t.Union[str, dict] = pydantic.Field(
        description="The string representation of the error"
    )

    @pydantic.model_validator(mode="before")
    def _parse_exception(cls, data: t.Any) -> t.Any:
        if isinstance(data, Exception):
            # still get nice formatting if it is our internal error class
            from spice_rack._bases._exception._exception_base import CustomExceptionBase
            if isinstance(data, CustomExceptionBase):
                data = {
                    "type": type(data).__name__,
                    "detail": data.get_error_payload_inst().json_dict()
                }

            else:
                data = {
                    "type": type(data).__name__,
                    "detail": str(data)
                }

        return data
