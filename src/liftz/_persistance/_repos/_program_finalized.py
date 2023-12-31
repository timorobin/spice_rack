from __future__ import annotations
from sqlalchemy import orm, ForeignKey

from liftz._persistance._repos._record_base import TableBase
from liftz._persistance._types import (
    ProgramTemplateKeyT,
    StrengthExerciseKeyT,
    TimestampT,
    UserIdT
)


__all__ = (
    "FinalizedStrengthSet",
    "FinalizedProgramRunRecord"
)

_SETS_TABLE_NAME = "finalized_strength_sets"
_PROGRAM_TABLE_NAME = "finalized_program_run"
_LINK_TABLE_NAME = "finalized_strength_sets_to_program_record"


class FinalizedStrengthSet(TableBase):
    """a set already finalized"""
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True
    )
    program_record_id: orm.Mapped[int] = orm.mapped_column(
        ForeignKey(f"{_PROGRAM_TABLE_NAME}.id")
    )
    exercise_key: orm.Mapped[StrengthExerciseKeyT] = orm.mapped_column(
        doc="key to the exercise info"
    )
    week: orm.Mapped[int] = orm.mapped_column(
        doc="the week this set is from"
    )
    day: orm.Mapped[int] = orm.mapped_column(
        doc="the day within the week"
    )
    weight_prescribed: orm.Mapped[float] = orm.mapped_column(
        doc="the weight prescribed"
    )
    reps_prescribed: orm.Mapped[int] = orm.mapped_column(
        doc="the reps prescribed"
    )
    weight_used: orm.Mapped[float] = orm.mapped_column(
        doc="the weight used"
    )
    reps_completed: orm.Mapped[int] = orm.mapped_column(
        doc="the reps completed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SETS_TABLE_NAME


class FinalizedProgramRunRecord(TableBase):
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True
    )
    template_key: orm.Mapped[ProgramTemplateKeyT] = orm.mapped_column(
        doc="key for the template this is an invocation of"
    )
    started_at: orm.Mapped[TimestampT] = orm.mapped_column(doc="when the program started")
    finished_at: orm.Mapped[TimestampT] = orm.mapped_column(
        doc="the timestamp when this program execution was finalized"
    )
    strength_sets: orm.Mapped[list[FinalizedStrengthSet]] = orm.relationship(
        cascade="all, delete-orphan",
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _PROGRAM_TABLE_NAME
