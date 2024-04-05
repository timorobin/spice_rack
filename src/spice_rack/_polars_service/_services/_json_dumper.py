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
        df: _types.PolarsMaybeLazyDfT,
) -> _types.RowDictsT:
    """
    dump the polars LazyFrame or DataFrame into json-encodeable list of dictionaries
    Args:
        df: LazyFrame or DataFrame instance

    Returns:
        a list of dicts
    """
    collected_df: pl.DataFrame
    if isinstance(df, pl.LazyFrame):
        collected_df = df.collect()  # noqa -- idk what p is
    else:
        collected_df = df

    df_json = collected_df.write_json(file=None, row_oriented=True)
    return json.loads(df_json)


def get_json_safe_column_dict(
        df: _types.PolarsMaybeLazyDfT
) -> _types.ColumnarDictT:
    """
    dump the polars LazyFrame or DataFrame into json-encodeable dict with keys being column names and values
    being lists containing the data for the given column.

    Args:
        df: LazyFrame or DataFrame instance

    Returns:
        a dict of lists
    """
    collected_df: pl.DataFrame
    if isinstance(df, pl.LazyFrame):
        collected_df = df.collect()  # noqa -- idk what p is
    else:
        collected_df = df

    df_json = collected_df.write_json(file=None, row_oriented=False)
    return json.loads(df_json)


def get_json_safe_row_dicts_lazy_peek(
        lazy_df: _types.PolarsLazyDfT, num_rows: int = 3
) -> _types.RowDictsT:
    """
    dump the first n rows of a polars LazyFrame into a json-encodeable list of dictionaries,
    without having to collect the entire LazyFrame.

    Args:
        lazy_df: LazyFrame instance
        num_rows: the number of rows to collect

    Returns:
        a list of dicts
    """
    sample_df = lazy_df.fetch(n_rows=num_rows)
    return get_json_safe_row_dicts(sample_df)


def get_json_safe_column_dict_lazy_peek(
        lazy_df: _types.PolarsMaybeLazyDfT, num_rows: int = 3
) -> _types.ColumnarDictT:
    """
    dump the first n rows of a polars LazyFrame into a json-encodeable dict with keys being column names and values
    being lists containing the data for the given column.

    Args:
        lazy_df: LazyFrame instance
        num_rows: the number of rows to collect

    Returns:
        a dict of lists
    """
    sample_df = lazy_df.fetch(n_rows=num_rows)
    return get_json_safe_column_dict(sample_df)
