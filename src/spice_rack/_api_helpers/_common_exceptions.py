from __future__ import annotations
from typing import Optional
from pydantic import Field

from spice_rack import _base_classes


__all__ = (
    "UnknownExceptionWrapper",
)


class _UnknownExceptionErrorInfo(_base_classes.exception.ErrorInfoBase):
    """
    An unexpected exception was encountered, i.e. not one of our subclasses.
    Wrapping it with this class allows us to work it into our exception handling and other
    tooling.
    """
    caught_exception: _base_classes.exception.types.WrappedExternalException = Field(
        description="the exception we encountered"
    )


class UnknownExceptionWrapper(
    _base_classes.exception.CustomExceptionBase[_UnknownExceptionErrorInfo]
):
    """
    An unexpected exception was encountered, i.e. not one of our subclasses.
    Wrapping it with this class allows us to work it into our
    exception handling and other tooling.

    Notes:
        - a custom "detail" can be specified, or left blank, in which case we use the str
          representation of the caught exception
    """
    def __init__(
            self,
            caught_exception: Exception,
            detail: Optional[str] = None,
            verbose: bool = True,
            extra_info: Optional[dict] = None
    ):
        error_info = {
            "caught_exception": caught_exception,
        }
        if detail is None:
            detail = str(caught_exception)
        super().__init__(
            detail=detail,
            error_info=error_info,
            extra_info=extra_info,
            verbose=verbose
        )
