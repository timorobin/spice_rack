from __future__ import annotations
from sqlmodel import Field, Relationship

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
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    program_record_id: int = Field(
        foreign_key=f"{_PROGRAM_TABLE_NAME}.id"
    )
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
        return _SETS_TABLE_NAME


class FinalizedProgramRunRecord(TableBase):
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True
    )
    template_key: ProgramTemplateKeyT = Field(
        description="key for the template this is an invocation of"
    )
    started_at: TimestampT = Field(description="when the program started")
    finished_at: TimestampT = Field(
        description="the timestamp when this program execution was finalized"
    )
    strength_sets: list[FinalizedStrengthSet] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _PROGRAM_TABLE_NAME
