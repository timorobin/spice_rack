from __future__ import annotations
from typing import TYPE_CHECKING, Type, Optional
from pydantic import Field

from spice_rack import _bases

if TYPE_CHECKING:
    from spice_rack._frozen_registry._base import FrozenRegistryBase


__all__ = (
    "ItemIndexInvalidException",
)


class _ItemIxInvalidErrorInfo(_bases.exceptions.ErrorInfoBase):
    """tried to get an item with an index int, but the int was invalid for this registry"""
    registry_type: str = Field(description="the name of the registry class that made this error")
    invalid_ix: int = Field(description="the index we tried, that was found invalid")
    registry_size: int = Field(description="the total size of this registry")
    caught_exception: _bases.exceptions.WrappedExternalException = Field(
        description="the exception we caught"
    )


class ItemIndexInvalidException(
    _bases.exceptions.CustomExceptionBase[_ItemIxInvalidErrorInfo]
):
    """tried to get an item with an index int, but the int was invalid for this registry"""
    def __init__(
            self,
            invalid_ix: int,
            registry_type: Type[FrozenRegistryBase],
            registry_size: int,
            caught_exception: Exception,
            verbose: bool = True,
            extra_info: Optional[dict] = None
    ):
        detail = (f"__getitem__ failed with index {invalid_ix}. "
                  f"The '{registry_type.__name__}' registry has {registry_size} items.")

        error_info = {
            "registry_type": registry_type.__name__,
            "invalid_ix": invalid_ix,
            "registry_size": registry_size,
            "caught_exception": caught_exception,
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )
