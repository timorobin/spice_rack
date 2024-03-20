from __future__ import annotations
from typing import TYPE_CHECKING, Type, Optional
from pydantic import Field

from spice_rack import _bases

if TYPE_CHECKING:
    from spice_rack._frozen_registry._base import FrozenRegistryBase

__all__ = (
    "KeyAlreadyExistsException",
)


class _KeyAlreadyExistsErrorInfo(_bases.exceptions.ErrorInfoBase):
    """trying to add item but something with that key already exists"""
    registry_type: str = Field(description="the name of the registry class that made this error")
    duplicate_key: str = Field(description="the key that already exists in this registry")


class KeyAlreadyExistsException(
    _bases.exceptions.CustomExceptionBase[_KeyAlreadyExistsErrorInfo]
):
    """trying to add item but something with that key already exists"""
    def __init__(
            self,
            duplicate_key: str,
            registry_type: Type[FrozenRegistryBase],
            verbose: bool = True,
            extra_info: Optional[dict] = None
    ):
        detail = f"an item with the key, '{duplicate_key}', already exists"

        error_info = {
            "registry_type": registry_type.__name__,
            "duplicate_key": duplicate_key,
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )
