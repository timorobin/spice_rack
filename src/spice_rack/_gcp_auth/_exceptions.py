from __future__ import annotations
import pydantic
from google.auth import exceptions as gcp_exceptions  # noqa

from spice_rack import _bases


__all__ = (
    "DefaultAuthNotAvailableException",
)


class _DefaultAuthNotAvailableErrorInfo(_bases.exceptions.ErrorInfoBase):
    gcp_error: _bases.exceptions.WrappedExternalException = pydantic.Field(
        description="error from the gcp auth external lib"
    )


class DefaultAuthNotAvailableException(_bases.exceptions.CustomExceptionBase[_DefaultAuthNotAvailableErrorInfo]):
    def __init__(
            self,
            detail: str,
            gcp_error: gcp_exceptions.GoogleAuthError,
    ):
        error_info = {
            "gcp_error": gcp_error
        }
        super().__init__(
            detail=detail if detail else str(gcp_error),
            error_info=error_info,
            verbose=True,
            extra_info=None
        )
