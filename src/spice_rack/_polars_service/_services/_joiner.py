from __future__ import annotations
import typing as t
import polars as pl

if t.TYPE_CHECKING:
    from spice_rack._polars_service import _types

__all__ = (
    "HowJoinT",
    "join_dfs",
    "stack_dfs",

)

HowJoinT = t.Literal["inner", "outer", "left"]


def join_dfs(
        dfs: t.Iterable[_types.PolarsMaybeLazyDfT],
        join_on: str,
        how: HowJoinT = "inner"
) -> _types.PolarsLazyDfT:
    """
    join an iterable of polars DataFrame or LazyFrame objects into a single LazyFrame

    Args:
        dfs: iterable of polars objects
        join_on: the column we are joining on, all dataframes must have this column
        how: the type of join, 'inner', 'outer', 'left',
            if 'left' the first dataframe in the iterable is the 'left' one

    Returns:
        pl.LazyFrame: the joined polars LazyFrame
    """
    merged_df: t.Optional[pl.DataFrame] = None
    for df in dfs:

        if isinstance(df, pl.DataFrame):
            df = df.lazy()
        if isinstance(df, pl.LazyFrame):
            df = df.collect()

        if merged_df is None:
            merged_df = df
        else:
            merged_df = merged_df.join(other=df, on=join_on, how=how)

    return merged_df.lazy()


def stack_dfs(
        dfs: t.List[_types.PolarsMaybeLazyDfT],
) -> _types.PolarsLazyDfT:
    """
    vertically stack an iterable of polars DataFrame or LazyFrame objects into a single LazyFrame.
    This is a vertical stack.

    Args:
        dfs: iterable of polars objects

    Returns:
        pl.LazyFrame: the stacked polars LazyFrame
    """

    if len(dfs) == 0:
        raise ValueError("empty list passed in")

    col_sets = {}
    for i, df_i in enumerate(dfs):
        col_sets[i] = list(df_i.columns)

    reference_cols = None
    for ix, cols in col_sets.items():
        if reference_cols is None:
            reference_cols = set(cols)
        else:
            if set(cols) != reference_cols:
                raise ValueError(f"columns must match to stack dfs, {col_sets}")

    # cast all dtypes to first df
    reference_schema = dfs[0].schema
    sorted_col_exprs = []
    for col in sorted(list(reference_cols)):
        dtype = reference_schema.get(col)
        if dtype is None:
            raise ValueError(f"'{col}' missing from reference schema?")
        expr = pl.col(col).cast(dtype)
        sorted_col_exprs.append(expr)

    dfs_to_stack = [
        df_i.lazy().select(sorted_col_exprs) for df_i in dfs
    ]
    return pl.concat(items=dfs_to_stack, how="vertical", ).lazy()
