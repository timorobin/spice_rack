from __future__ import annotations
import typing as t
import pydantic
import pydantic_core
import polars as pl

from spice_rack._polars_service._types import _dicts, _discrim_helper


__all__ = (
    "PolarsLazyDfT",
    "PolarsLazyDfTypeAdapter"
)


class _PolarsLazyDfPydanticAnnotation:
    @classmethod
    def _get_lazy_df_schema(cls) -> pydantic_core.CoreSchema:
        """already a lazy df"""
        return pydantic_core.core_schema.is_instance_schema(
            cls=pl.LazyFrame,
            cls_repr="pl.LazyFrame",
            ref="polars_lazy_dataframe",
        )

    @classmethod
    def _get_df_schema(cls) -> pydantic_core.CoreSchema:
        return pydantic_core.core_schema.chain_schema(
            [
                pydantic_core.core_schema.is_instance_schema(
                    cls=pl.DataFrame,
                    cls_repr="pl.DataFrame",
                    ref="polars_dataframe",
                ),
                pydantic_core.core_schema.no_info_plain_validator_function(
                    function=lambda _collected_df: _collected_df.lazy()
                )
            ]
        )

    @classmethod
    def _get_row_dicts_schema(cls) -> pydantic_core.CoreSchema:
        return pydantic_core.core_schema.chain_schema(
            [
                _dicts.RowDictsTypeAdapter.core_schema,
                pydantic_core.core_schema.no_info_plain_validator_function(
                    function=lambda _rows: pl.DataFrame(_rows).lazy()
                ),
            ]
        )

    @classmethod
    def _get_columnar_dict_schema(cls) -> pydantic_core.CoreSchema:
        return pydantic_core.core_schema.chain_schema(
            [
                _dicts.ColumnarDictTypeAdapter.core_schema,
                pydantic_core.core_schema.no_info_plain_validator_function(
                    function=lambda _column_data: pl.DataFrame(_column_data).lazy()
                ),
            ]
        )

    @classmethod
    def _get_core_json_schema(cls) -> pydantic_core.CoreSchema:
        """
        return the schema we use for json serialization and deserialization.
        """
        return _dicts.RowDictsJsonDumpedTypeAdapter.core_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: pydantic.GetCoreSchemaHandler,
    ) -> pydantic_core.core_schema.CoreSchema:
        """
        creates a pydantic core schema that behaves in the following ways

        * LazyFrame instance will be parsed as a LazyFrame instance, unchanged
        * DataFrame instance will be cast to a LazyFrame.
        * list of dicts will be parsed as a LazyFrame. (row orientation)
        * dict of lists will be parsed as a LazyFrame (columnar orientation)

        * serialization will return a row orientation of json-encodeable dicts, only the first 3

        Args:
            _source_type: the class calling this, not sure exactly what it means beyond that,
                pydantic expects it.
            _handler: another param pydantic expected

        Returns:
            pydantic_core.core_schema.CoreSchema
        """
        from spice_rack._polars_service import _services

        choices = _discrim_helper.build_choices(
            df_schema=cls._get_df_schema(),
            lazy_df_schema=cls._get_lazy_df_schema(),
            row_dicts_schema=cls._get_row_dicts_schema(),
            columnar_dict_schema=cls._get_columnar_dict_schema()
        )

        return pydantic_core.core_schema.json_or_python_schema(
            python_schema=pydantic_core.core_schema.tagged_union_schema(
              choices=choices, discriminator=_discrim_helper.discrim_func
            ),
            serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(

                # todo: how could we make num_rows variable?
                lambda _df: _services.get_json_safe_row_dicts_lazy_peek(_df, num_rows=3),

                when_used="json-unless-none"
            ),
            json_schema=cls._get_core_json_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            _core_schema: pydantic_core.core_schema.CoreSchema,
            handler: pydantic.GetJsonSchemaHandler
    ):
        """
        copy the row schema
        """
        return handler(cls._get_core_json_schema())


PolarsLazyDfT = t.Annotated[
    pl.LazyFrame,
    _PolarsLazyDfPydanticAnnotation
]
"""
An annotated type representing a polars LazyFrame.

This extra metadata allows us to include polars lazy dataframes in the pydantic ecosystem, 
e.g. as a field on a model. The pydantic behavior is as follows:

* LazyFrame instance will be parsed as a LazyFrame instance, unchanged
* DataFrame instance will be cast to a LazyFrame.
* list of dicts will be parsed as a LazyFrame. (row orientation)
* dict of lists will be parsed as a LazyFrame (columnar orientation)

* serialization will return a row orientation of json-encodeable dicts, only the first 3

Notes: this is not safe for roundtrip serialization, i.e. the a serialized instance of an instance
    of this type will not necessarily deserialize to be equal to the original instance
"""

PolarsLazyDfTypeAdapter: pydantic.TypeAdapter[PolarsLazyDfT] = pydantic.TypeAdapter(PolarsLazyDfT)
"""
type adapter for PolarsLazyDfT
"""
