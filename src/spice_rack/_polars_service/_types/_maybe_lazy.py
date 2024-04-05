from __future__ import annotations
import typing as t
import pydantic
import polars as pl

from spice_rack._polars_service._types import _collected_df, _lazy_df


__all__ = (
    "PolarsMaybeLazyDfT",
    "PolarsMaybeLazyDfTypeAdapter",
    "PolarsDfTV"
)


def _callable_discrim(_obj: t.Any) -> t.Literal["collected", "lazy"]:
    if isinstance(_obj, pl.LazyFrame):
        return "lazy"
    else:
        return "collected"


PolarsMaybeLazyDfT = t.Annotated[
    t.Union[
        t.Annotated[_collected_df.PolarsDfT, pydantic.Tag("collected")],
        t.Annotated[_lazy_df.PolarsLazyDfT, pydantic.Tag("lazy")],
    ],
    pydantic.Discriminator(discriminator=_callable_discrim)
]
"""
An annotated type representing a union of polars DataFrame or LazyFrame.

This extra metadata allows us to include polars collected dataframes in the pydantic ecosystem, 
e.g. as a field on a model. The pydantic behavior is as follows:

* A LazyFrame instance will be kept as a LazyFrame instance, unchanged
* DataFrame instance will be parsed as a DataFrame instance, unchanged
* list of dicts will be parsed as a DataFrame. (row orientation)
* dict of lists will be parsed as a DataFrame (columnar orientation)

* serialization will return a row orientation of json-encodeable dicts, if lazy, only the first 3

Notes: this is not safe for roundtrip serialization, i.e. the a serialized instance of an instance
    of this type will not necessarily deserialize to be equal to the original instance
"""

PolarsMaybeLazyDfTypeAdapter: pydantic.TypeAdapter[PolarsMaybeLazyDfT] = pydantic.TypeAdapter(PolarsMaybeLazyDfT)
"""
type adapter for PolarsMaybeLazyDfT
"""

PolarsDfTV = t.TypeVar("PolarsDfTV", _collected_df.PolarsDfT, _lazy_df.PolarsLazyDfT)
"""common type var that could be either a lazy or collected dataframe"""
