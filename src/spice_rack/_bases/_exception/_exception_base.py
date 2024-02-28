from __future__ import annotations
import types
import typing as t
from devtools import pformat

from spice_rack._bases._exception import _error_info, _exception_exception


__all__ = (
    "CustomExceptionBase",
)


Self = t.TypeVar("Self", bound="CustomExceptionBase")
"""pycharm type checker supports this, but it is same as new 'Self' type ann"""

ErrorInfoTV = t.TypeVar("ErrorInfoTV", bound=_error_info.ErrorInfoBase)


class CustomExceptionBase(Exception, t.Generic[ErrorInfoTV]):
    """
    Base for a custom-built exception class.

    Note:
        the typing for the
    """
    _error_info_cls: t.ClassVar[t.Type[_error_info.ErrorInfoBase]] = None  # type: ignore

    _detail: str
    _verbose: bool
    _error_info_inst: ErrorInfoTV

    def __class_getitem__(cls, item: t.Union[t.TypeVar, t.Type[_error_info.ErrorInfoBase]]):

        error_info_cls: t.Type[_error_info.ErrorInfoBase]

        # if manually set, just keep that
        if cls._error_info_cls is not None:
            error_info_cls = cls._error_info_cls
        else:
            try:
                if isinstance(item, t.TypeVar):
                    # if a type var, make sure we have a bound, and use that
                    if item.__bound__:
                        error_info_cls = item.__bound__
                    else:
                        raise ValueError(
                            f"'{item}' is a type var, and must have a bound set"
                        )

                elif issubclass(item, _error_info.ErrorInfoBase):
                    error_info_cls = item

                else:
                    raise ValueError(f"unable to set error info class from the item, {item}")

            except Exception as e:
                raise ValueError(
                    f"error encountered trying to get error info class from type var, error: {e}"
                ) from e

        intermediate_cls_name = f"{cls.__name__}__{item.__name__}"
        new_cls: t.Type[CustomExceptionBase] = t.cast(
            t.Type[CustomExceptionBase],
            types.new_class(
                intermediate_cls_name, bases=(cls, ),
                kwds={"error_info_cls": error_info_cls}
            )
        )
        return new_cls

    def __init_subclass__(
            cls,
            error_info_cls: t.Optional[t.Type[_error_info.ErrorInfoBase]] = None,
            **kwargs
    ):
        if error_info_cls is None and cls._error_info_cls is None:
            raise ValueError(f"{cls.__name__} must specify error info class'")
        elif error_info_cls is not None:
            cls._error_info_cls = error_info_cls
        super().__init_subclass__(**kwargs)

    def __init__(
            self,
            detail: str,
            error_info: t.Union[ErrorInfoTV, dict],
            verbose: bool,
            extra_info: t.Optional[dict]
    ):
        self._detail = detail
        self._verbose = verbose

        try:
            self._error_info_inst = self.get_error_info_cls().validate(error_info)

        except Exception as e:
            raise _exception_exception.CustomExceptionInitializationError(
                detail="error info provided failed validation",
                caught_exception=e
            ) from e

        if extra_info:
            self._error_info_inst.extra.update(extra_info)
        formatted_str: str
        if self.verbose:
            formatted_str = self._get_formatted_str_verbose()
        else:
            formatted_str = self._get_formatted_str_terse()

        super().__init__(formatted_str)

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def verbose(self) -> bool:
        return self._verbose

    @property
    def error_info(self: Self) -> ErrorInfoTV:
        return self._error_info_inst

    @classmethod
    def get_error_info_cls(cls: t.Type[Self]) -> t.Type[ErrorInfoTV]:
        return cls._error_info_cls  # type: ignore

    # this should be the generic type, but it isn't working
    # _error_info.ErrorPayload[ErrorInfoTV]:

    @classmethod
    def get_error_payload_schema_title(cls) -> t.Optional[str]:
        """
        overwrite this to customize the title of schema of the payload class.
        default is to return None and not customize it
        """
        return None

    @classmethod
    @t.final
    def get_error_payload_cls(cls: t.Type[Self]) -> t.Type[_error_info.ErrorPayload[ErrorInfoTV]]:
        """
        Returns: an ErrorPayload class parameterized with the correct
        concrete subclass of ErrorInfoBase
        """
        payload_cls = _error_info.ErrorPayload[cls.get_error_info_cls()]  # type: ignore
        custom_schema_title = cls.get_error_payload_schema_title()
        if custom_schema_title:
            payload_cls.set_schema_title(custom_schema_title)
        return payload_cls

    @t.final
    def get_error_payload_inst(self: Self) -> _error_info.ErrorPayload[ErrorInfoTV]:
        return _error_info.ErrorPayload(
            detail=self.detail,
            error_type=type(self).__name__,
            info=self.error_info,
        )

    def _get_formatted_str_verbose(self) -> str:
        return pformat(self.get_error_payload_inst().json_dict(use_str_fallback=True))

    def _get_formatted_str_terse(self) -> str:
        return self.detail
