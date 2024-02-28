from __future__ import annotations

from devtools import pformat

__all__ = (
    "CustomExceptionInitializationError",
)


class CustomExceptionInitializationError(Exception):
    """
    this is raised when we encounter an exception in our custom exception class

    Notes:
        - This is NOT a subclass of our custom exception base class, so if we have a problem
          with our base class we won't end up in recursive spiral
    """

    def __init__(
            self,
            detail: str,
            caught_exception: Exception
    ):

        data_dict = {
            "detail": detail,
            "exception_type": type(caught_exception).__name__,
            "exception_detail": str(caught_exception)
        }
        super().__init__(pformat(data_dict))
