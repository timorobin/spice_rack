from __future__ import annotations
import typing as t
from sqlmodel import Field

from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    StrengthExerciseKeyT,
    UserIdT
)


__all__ = (
    "StrengthExerciseRecord",
)


class StrengthExerciseRecord(_record_base.TableBase, table=True):
    """record of strength exercises"""
    user_id: t.Optional[UserIdT] = Field(
        description="the id of the user connected to this record, "
                    "if none this is a system-level record",
        index=True,
    )
    key: StrengthExerciseKeyT = Field(
        description="the key", primary_key=True
    )
    description: str = Field(
        description="description",

    )
    # tags: orm.Mapped[ExerciseTagsEnumT] = Field(
    #     ARRAY(Enum),
    #     description="list of tags for this exercise"
    # )

    @classmethod
    def get_table_name(cls) -> str:
        return "strength_exercises"
