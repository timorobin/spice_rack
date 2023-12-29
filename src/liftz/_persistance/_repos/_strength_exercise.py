from __future__ import annotations
from sqlalchemy import orm

from liftz import _models
from liftz._persistance._repos import _record_base


__all__ = (
    "StrengthExerciseRecord",
)


_KeyT = str
_ExerciseTagsEnumT = _models.strength_exercise.StrengthExerciseTags


class StrengthExerciseRecord(_record_base.TableBase):
    """record of strength exercises"""
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )

    key: orm.Mapped[_KeyT] = orm.mapped_column(
        doc="the key", primary_key=True
    )
    tags: orm.Mapped[_ExerciseTagsEnumT] = orm.mapped_column(
        doc="list of tags for this exercise"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "strength_exercises"
