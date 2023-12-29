from __future__ import annotations
from typing import Optional
from sqlalchemy import orm

from liftz._persistance._repos._record_base import TableBase
from liftz._persistance._types import (
    ProgramTemplateKeyT,
    StrengthExerciseKeyT,
    TimestampT,
    UserIdT
)


__all__ = (
    "StrengthSetNotStarted",
    "StrengthSetInProgress",
    "StrengthSetFinished",
    "ActiveProgramRecord"
)

_SET_NOT_STARTED = "active_program_strength_sets_not_started"
_SET_IN_PROG = "active_program_strength_sets_in_progress"
_SET_FINISHED = "active_program_strength_sets_finished"
_PROGRAM = "active_programs"


class StrengthSetNotStarted(TableBase):
    """a set that is part of a day we haven't started"""
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True
    )
    program_record: orm.Mapped[ActiveProgramRecord] = orm.relationship(
        back_populates="strength_sets_not_started",
    )
    exercise_key: orm.Mapped[StrengthExerciseKeyT] = orm.mapped_column(
        doc="the key to the exercise"
    )
    week: orm.Mapped[int] = orm.mapped_column(
        doc="the week this set is from",
        index=True
    )
    day: orm.Mapped[int] = orm.mapped_column(
        doc="the day within the week",
        index=True
    )
    weight: orm.Mapped[float] = orm.mapped_column(
        doc="the weight prescribed"
    )
    reps: orm.Mapped[int] = orm.mapped_column(
        doc="the reps prescribed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_NOT_STARTED


class StrengthSetInProgress(TableBase):
    """a set that is part of an in-progress day"""
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True
    )
    program_record: orm.Mapped[ActiveProgramRecord] = orm.relationship(
        back_populates="strength_sets_in_progress",
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
    weight_used: orm.Mapped[Optional[float]] = orm.mapped_column(
        doc="the weight used", default=None
    )
    reps_completed: orm.Mapped[Optional[int]] = orm.mapped_column(
        doc="the reps completed", default=None
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_IN_PROG


class StrengthSetFinished(TableBase):
    """
    A set already finalized. These are not the sets of the current day already
    finished. These are sets of days that are already finalized.
    """
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True
    )
    program_record: orm.Mapped[ActiveProgramRecord] = orm.relationship(
        back_populates="strength_sets_finished",
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
        return _SET_FINISHED


class ActiveProgramRecord(TableBase):
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
    started_at: orm.Mapped[TimestampT] = orm.mapped_column(
        doc="when the program started"
    )
    updated_at: orm.Mapped[TimestampT] = orm.mapped_column(
        doc="last time we executed a day of this program"
    )

    strength_sets_not_started: list[StrengthSetNotStarted] = orm.relationship(
        cascade="all, delete-orphan",
        back_populates="program_record"
    )

    strength_sets_in_progress: list[StrengthSetInProgress] = orm.relationship(
        cascade="all, delete-orphan",
        back_populates="program_record"
    )

    strength_sets_finished: list[StrengthSetFinished] = orm.relationship(
        cascade="all, delete-orphan",
        back_populates="program_record"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _PROGRAM
