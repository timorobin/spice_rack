from __future__ import annotations
import typing as t
from typing_extensions import TypeAlias
from pydantic import Field

from spice_rack import _bases

if t.TYPE_CHECKING:
    from spice_rack._frozen_registry._base import FrozenRegistryBase

__all__ = (
    "DuplicateKeysInRegistryException",
)


_DupeKeyCountsT: TypeAlias = dict[str, int]


class _DuplicateKeysInRegistryErrorInfo(_bases.exceptions.ErrorInfoBase):
    """duplicate keys found in the registry"""
    registry_type: str = Field(description="the name of the registry class that made this error")
    duplicates_with_counts: _DupeKeyCountsT = Field(
        description="a dict of keys that are duplicate and the number of times they appear"
    )


class DuplicateKeysInRegistryException(
    _bases.exceptions.CustomExceptionBase[_DuplicateKeysInRegistryErrorInfo]
):
    """duplicate keys found in the registry"""
    def __init__(
            self,
            registry_type: t.Type[FrozenRegistryBase],
            duplicate_keys: _DupeKeyCountsT,
            verbose: bool = True,
            extra_info: t.Optional[dict] = None
    ):
        detail = f"{len(duplicate_keys)} found in the '{registry_type.__name__}' registry"
        error_info = {
            "registry_type": registry_type.__name__,
            "duplicates_with_counts": duplicate_keys,
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )
