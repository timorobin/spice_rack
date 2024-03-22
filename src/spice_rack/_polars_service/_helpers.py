from __future__ import annotations
import json
import typing as t
import polars as pl

if t.TYPE_CHECKING:
    from spice_rack._polars_service import _types


__all__ = (
    "get_json_safe_row_dicts",
    "get_json_safe_column_dict",
    "get_json_safe_row_dicts_lazy_peek",
    "get_json_safe_column_dict_lazy_peek"
)


def get_json_safe_row_dicts(
        df: t.Union[pl.DataFrame, pl.LazyFrame],
) -> _types.RowDictsT:
    collected_df: pl.DataFrame
    if isinstance(df, pl.LazyFrame):
        collected_df = df.collect()  # noqa -- idk what p is
    else:
        collected_df = df

    df_json = collected_df.write_json(file=None, row_oriented=True)
    return json.loads(df_json)


def get_json_safe_column_dict(
        df: t.Union[pl.DataFrame, pl.LazyFrame]
) -> _types.ColumnarDictT:
    collected_df: pl.DataFrame
    if isinstance(df, pl.LazyFrame):
        collected_df = df.collect()  # noqa -- idk what p is
    else:
        collected_df = df

    df_json = collected_df.write_json(file=None, row_oriented=False)
    return json.loads(df_json)


def get_json_safe_row_dicts_lazy_peek(
        lazy_df: pl.LazyFrame, num_rows: int = 3
) -> _types.RowDictsT:
    sample_df = lazy_df.fetch(n_rows=num_rows)
    return get_json_safe_row_dicts(sample_df)


def get_json_safe_column_dict_lazy_peek(
        lazy_df: pl.LazyFrame, num_rows: int = 3
) -> _types.ColumnarDictT:
    sample_df = lazy_df.fetch(n_rows=num_rows)
    return get_json_safe_column_dict(sample_df)
