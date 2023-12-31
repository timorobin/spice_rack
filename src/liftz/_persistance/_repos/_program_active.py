from __future__ import annotations
from typing import Optional
from sqlmodel import Field, Relationship

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
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    program_record_id: Optional[int] = Field(foreign_key=f"{_PROGRAM}.id")
    exercise_key: StrengthExerciseKeyT = Field(
        description="the key to the exercise"
    )
    week: int = Field(
        description="the week this set is from",
        index=True
    )
    day: int = Field(
        description="the day within the week",
        index=True
    )
    weight: float = Field(
        description="the weight prescribed"
    )
    reps: int = Field(
        description="the reps prescribed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_NOT_STARTED


class StrengthSetInProgress(TableBase):
    """a set that is part of an in-progress day"""
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    program_record_id: int = Field(foreign_key=f"{_PROGRAM}.id")

    exercise_key: StrengthExerciseKeyT = Field(
        description="key to the exercise info"
    )
    week: int = Field(
        description="the week this set is from"
    )
    day: int = Field(
        description="the day within the week"
    )
    weight_prescribed: float = Field(
        description="the weight prescribed"
    )
    reps_prescribed: int = Field(
        description="the reps prescribed"
    )
    weight_used: Optional[float] = Field(
        description="the weight used", default=None
    )
    reps_completed: Optional[int] = Field(
        description="the reps completed", default=None
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_IN_PROG


class StrengthSetFinished(TableBase):
    """
    A set already finalized. These are not the sets of the current day already
    finished. These are sets of days that are already finalized.
    """
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    program_record_id: int = Field(foreign_key=f"{_PROGRAM}.id")

    exercise_key: StrengthExerciseKeyT = Field(
        description="key to the exercise info"
    )
    week: int = Field(
        description="the week this set is from"
    )
    day: int = Field(
        description="the day within the week"
    )
    weight_prescribed: float = Field(
        description="the weight prescribed"
    )
    reps_prescribed: int = Field(
        description="the reps prescribed"
    )
    weight_used: float = Field(
        description="the weight used"
    )
    reps_completed: int = Field(
        description="the reps completed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_FINISHED


class ActiveProgramRecord(TableBase):
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    template_key: ProgramTemplateKeyT = Field(
        description="key for the template this is an invocation of"
    )
    started_at: TimestampT = Field(
        description="when the program started"
    )
    updated_at: TimestampT = Field(
        description="last time we executed a day of this program"
    )

    strength_sets_not_started: list[StrengthSetNotStarted] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    strength_sets_in_progress: list[StrengthSetInProgress] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    strength_sets_finished: list[StrengthSetFinished] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _PROGRAM
