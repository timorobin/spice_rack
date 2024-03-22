from __future__ import annotations
import typing as t
import polars as pl

import pydantic_core

__all__ = (
    "build_choices",
    "discrim_func"
)

_ChoicesT = t.Literal["df", "lazy_df", "row_dicts", "columnar_dict"]


def build_choices(
        df_schema: pydantic_core.CoreSchema,
        lazy_df_schema: pydantic_core.CoreSchema,
        row_dicts_schema: pydantic_core.CoreSchema,
        columnar_dict_schema: pydantic_core.CoreSchema
) -> t.Dict[_ChoicesT, pydantic_core.CoreSchema]:
    return {
        "df": df_schema,
        "lazy_df": lazy_df_schema,
        "row_dicts": row_dicts_schema,
        "columnar_dict": columnar_dict_schema,
    }


def discrim_func(_obj: t.Any) -> _ChoicesT:
    if isinstance(_obj, pl.DataFrame):
        return "df"
    elif isinstance(_obj, pl.LazyFrame):
        return "lazy_df"
    elif isinstance(_obj, list):
        return "row_dicts"
    elif isinstance(_obj, dict):
        return "columnar_dict"
    else:
        raise ValueError(f"unable to parse '{type(_obj)}' as a polars dataframe")
