from __future__ import annotations
import types
from typing import Optional, Generic, TypeVar, Type, final, Union, ClassVar, cast, TYPE_CHECKING
from devtools import pformat

from spice_rack._base_classes._exception import _error_info, _exception_exception, _types

if TYPE_CHECKING:
    from spice_rack._base_classes._exception import _http


__all__ = (
    "CustomExceptionBase",
)


ErrorInfoTV = TypeVar("ErrorInfoTV", bound=_error_info.ErrorInfoBase)


class CustomExceptionBase(Exception, Generic[ErrorInfoTV]):
    """
    Base for a custom-built exception class.

    Note:
        the typing for the
    """
    # will be set in the '__class_getitem__' method
    _error_info_cls: ClassVar[Type[_error_info.ErrorInfoBase]] = None

    _detail: str
    _verbose: bool
    _error_info_inst: ErrorInfoTV

    def __class_getitem__(cls, item: Union[TypeVar, Type[_error_info.ErrorInfoBase]]):

        error_info_cls: Type[_error_info.ErrorInfoBase]

        # if manually set, just keep that
        if cls._error_info_cls is not None:
            error_info_cls = cls._error_info_cls
        else:
            try:
                if isinstance(item, TypeVar):
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
        new_cls: Type[CustomExceptionBase] = cast(
            Type[CustomExceptionBase],
            types.new_class(
                intermediate_cls_name, bases=(cls, ),
                kwds={"error_info_cls": error_info_cls}
            )
        )
        return new_cls

    def __init_subclass__(
            cls,
            error_info_cls: Optional[Type[_error_info.ErrorInfoBase]] = None,
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
            error_info: Union[ErrorInfoTV, dict],
            verbose: bool,
            extra_info: Optional[dict]
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
    def error_info(self) -> ErrorInfoTV:
        return self._error_info_inst

    @classmethod
    def get_error_info_cls(cls) -> Type[ErrorInfoTV]:
        return cls._error_info_cls

    # this should be the generic type, but it isn't working
    # _error_info.ErrorPayload[ErrorInfoTV]:

    @classmethod
    def get_error_payload_schema_title(cls) -> Optional[str]:
        """
        overwrite this to customize the title of schema of the payload class.
        default is to return None and not customize it
        """
        return None

    @classmethod
    @final
    def get_error_payload_cls(cls) -> Type[_error_info.ErrorPayload[_error_info.ErrorInfoBase]]:
        """
        Returns: an ErrorPayload class parameterized with the correct
        concrete subclass of ErrorInfoBase
        """
        payload_cls = _error_info.ErrorPayload[cls.get_error_info_cls()]
        custom_schema_title = cls.get_error_payload_schema_title()
        if custom_schema_title:
            payload_cls.set_schema_title(custom_schema_title)
        return payload_cls

    @classmethod
    @final
    def build_http_response_info_inst(
            cls,
            status_code: _types.HttpStatusCodeOrIntT,
            custom_desc: Optional[str] = None
    ) -> _http.HttpErrorResponseInfo:
        """
        Build a HttpErrorResponseInfo inst for this exception class.
        Use this when you want to assign a schema to a given status code for endpoint
        """
        from spice_rack._base_classes._exception import _http
        return _http.HttpErrorResponseInfo(
            status_code=status_code,
            exception_type=cls,
            custom_desc=custom_desc
        )

    @final
    def get_error_payload_inst(self) -> _error_info.ErrorPayload[_error_info.ErrorInfoBase]:
        return _error_info.ErrorPayload(
            detail=self.detail,
            error_type=type(self).__name__,
            info=self.error_info,
        )

    # todo: remove one of 'as_http_error_resp' and 'as_http_error'
    # return type ann should be ErrorInfoTV but using type var messes up PyCharm's type checking

    @final
    def as_http_error_resp(
            self,
            status_code: _types.HttpStatusCodeOrIntT,
    ) -> _http.HttpErrorResponse[_error_info.ErrorInfoBase]:
        from spice_rack._base_classes._exception import _http
        return _http.HttpErrorResponse[self.get_error_info_cls()](
            status_code=status_code,
            error_payload=self.get_error_payload_inst(),
        )

    @final
    def as_http_error(
            self,
            status_code: _types.HttpStatusCodeOrIntT
    ) -> _http.HttpException[_error_info.ErrorInfoBase]:
        from spice_rack._base_classes._exception import _http
        return _http.HttpException[self.get_error_info_cls()](
            status_code=status_code,
            error_payload=self.get_error_payload_inst(),
        )

    def _get_formatted_str_verbose(self) -> str:
        return pformat(self.get_error_payload_inst().json_dict(use_str_fallback=True))

    def _get_formatted_str_terse(self) -> str:
        return self.detail
