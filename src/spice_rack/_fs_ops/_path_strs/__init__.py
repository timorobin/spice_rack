import typing as t
import pydantic

from spice_rack._fs_ops._path_strs._base import *
from spice_rack._fs_ops._path_strs._abs import *
from spice_rack._fs_ops._path_strs._rel import *


_TagsT = t.Literal["rel", "abs"]


def _discrim(raw_str: str) -> _TagsT:
    if raw_str.startswith("/"):
        return "abs"
    else:
        return "rel"


RelOrAbsFilePathT = t.Annotated[
    t.Union[
        t.Annotated[AbsoluteFilePathStr, pydantic.Tag("abs")],
        t.Annotated[RelFilePathStr, pydantic.Tag("rel")],
    ],
    pydantic.Discriminator(_discrim)
]
RelOrAbsFilePathTypeAdapter: pydantic.TypeAdapter[RelOrAbsFilePathT] = pydantic.TypeAdapter(
    RelOrAbsFilePathT
)


RelOrAbsDirPathT = t.Annotated[
    t.Union[
        t.Annotated[AbsoluteDirPathStr, pydantic.Tag("abs")],
        t.Annotated[RelDirPathStr, pydantic.Tag("rel")],
    ],
    pydantic.Discriminator(_discrim)
]


RelOrAbsDirPathTypeAdapter: pydantic.TypeAdapter[RelOrAbsDirPathT] = pydantic.TypeAdapter(
    RelOrAbsDirPathT
)
