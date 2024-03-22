from __future__ import annotations
from uuid import uuid4
import pydantic


__all__ = (
    "GuidT", "GuidTypeAdapter", "gen_guid", "gen_str_guid"
)


GuidT = pydantic.UUID4

GuidTypeAdapter = pydantic.TypeAdapter(GuidT)


def gen_guid() -> GuidT:
    return uuid4()


def gen_str_guid() -> str:
    return gen_guid().hex
