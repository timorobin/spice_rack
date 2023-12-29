from __future__ import annotations
from sqlalchemy import orm

from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    StrengthExerciseKeyT,
    ExerciseTagsEnumT
)

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

    key: orm.Mapped[StrengthExerciseKeyT] = orm.mapped_column(
        doc="the key", primary_key=True
    )
    tags: orm.Mapped[ExerciseTagsEnumT] = orm.mapped_column(
        doc="list of tags for this exercise"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "strength_exercises"
