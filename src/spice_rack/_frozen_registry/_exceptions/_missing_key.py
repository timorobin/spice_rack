from __future__ import annotations
from typing import TYPE_CHECKING, Type, Optional
from pydantic import Field

from spice_rack import _bases

if TYPE_CHECKING:
    from spice_rack._frozen_registry._base import FrozenRegistryBase

__all__ = (
    "KeyNotFoundException",
)


class _KeyNotFoundErrorInfo(_bases.exceptions.ErrorInfoBase):
    """the specified key wasn't found in the registry"""
    registry_type: str = Field(description="the name of the registry class that made this error")
    missing_key: str = Field(description="the key we tried to find")
    keys_in_registry: list[str] = Field(description="the keys that are present")


class KeyNotFoundException(
    _bases.exceptions.CustomExceptionBase[_KeyNotFoundErrorInfo]
):
    """the specified key wasn't found in the registry"""
    def __init__(
            self,
            missing_key: str,
            registry_type: Type[FrozenRegistryBase],
            keys_in_registry: list[str],
            verbose: bool = True,
            extra_info: Optional[dict] = None
    ):
        detail = (f"failed to find the key, '{missing_key}', "
                  f"in the '{registry_type.__name__}' registry")

        error_info = {
            "registry_type": registry_type.__name__,
            "missing_key": missing_key,
            "keys_in_registry": keys_in_registry,
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )
