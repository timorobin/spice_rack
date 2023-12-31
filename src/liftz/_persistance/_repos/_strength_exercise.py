from __future__ import annotations
import typing as t
from sqlalchemy import orm, ARRAY, Enum

from liftz import _models
from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    StrengthExerciseKeyT,
    ExerciseTagsEnumT,
    UserIdT
)

if t.TYPE_CHECKING:
    from liftz._persistance._engine_builder import SessionT


__all__ = (
    "StrengthExerciseRecord",
)


class StrengthExerciseRecord(_record_base.TableBase):
    """record of strength exercises"""
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[t.Optional[UserIdT]] = orm.mapped_column(
        doc="the id of the user connected to this record, if none this is a system-level record",
        index=True,
    )
    key: orm.Mapped[StrengthExerciseKeyT] = orm.mapped_column(
        doc="the key", primary_key=True
    )
    description: orm.Mapped[str] = orm.mapped_column(
        doc="description",

    )
    tags: orm.Mapped[_models.strength_exercise.StrengthExerciseTags] = orm.mapped_column(
        ARRAY(Enum),
        doc="list of tags for this exercise"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "strength_exercises"
