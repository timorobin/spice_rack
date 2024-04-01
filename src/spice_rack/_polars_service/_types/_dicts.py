from __future__ import annotations
import typing as t
import pydantic

__all__ = (
    "ColumnarDictT", "ColumnarDictTypeAdapter",
    "RowDictsT", "RowDictsTypeAdapter",

    "RowDictsJsonDumpedT", "RowDictsJsonDumpedTypeAdapter",
    "ColumnarDictJsonDumpedT", "ColumnarDictJsonDumpedTypeAdapter"

)


ColumnarDictT = t.Dict[str, t.List[t.Any]]
ColumnarDictTypeAdapter = pydantic.TypeAdapter(ColumnarDictT)

RowDictsT = t.List[t.Dict[str, t.Any]]
RowDictsTypeAdapter = pydantic.TypeAdapter(RowDictsT)

RowDictsJsonDumpedT = t.List[t.Dict[str, pydantic.JsonValue]]
RowDictsJsonDumpedTypeAdapter = pydantic.TypeAdapter(RowDictsJsonDumpedT)

ColumnarDictJsonDumpedT = t.Dict[str, t.List[pydantic.JsonValue]]
ColumnarDictJsonDumpedTypeAdapter = pydantic.TypeAdapter(ColumnarDictJsonDumpedT)
