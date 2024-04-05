from __future__ import annotations
from uuid import uuid4
import pydantic


__all__ = (
    "GuidT", "GuidTypeAdapter", "gen_guid", "gen_str_guid"
)


GuidT = pydantic.UUID4
"""the pydantic type for UUID4"""

GuidTypeAdapter: pydantic.TypeAdapter[GuidT] = pydantic.TypeAdapter(GuidT)
"""a type adapter that validates strings to 'GuidT' instances"""


def gen_guid() -> GuidT:
    """generate a new UUID4"""
    return uuid4()


def gen_str_guid() -> str:
    """generate a new UUID4 hex"""

    return gen_guid().hex
