from __future__ import annotations
from typing import Optional
from pydantic import Field
from sqlmodel import Relationship

import spice_rack
from liftz._repos._record_base import TableBase
from liftz import _models

_ProgramTemplateKey = _models.program_template.components.ProgramTemplateKey
_ProgramTemplateTags = _models.program_template.components.ProgramTemplateTags


__all__ = (
    "StrengthSetNotStarted",
    "StrengthSetInProgress",
    "StrengthSetFinished"
)

_SET_NOT_STARTED = "active_program_strength_sets_not_started"
_SET_IN_PROG = "active_program_strength_sets_in_progress"
_SET_FINISHED = "active_program_strength_sets_finished"
_PROGRAM = "active_programs"


class StrengthSetNotStarted(TableBase):
    """a set that is part of a day we haven't started"""
    execution_guid: spice_rack.guid.GuidStr = Field(
        description="the guid to the execution record"
    )
    exercise_key: _models.strength_exercise.StrengthExerciseKey
    week: int
    day: int
    weight: float
    reps: int

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_NOT_STARTED


class StrengthSetInProgress(TableBase):
    """a set that is part of an in-progress day"""
    exercise_key: _models.strength_exercise.StrengthExerciseKey
    week: int
    day: int
    weight_prescribed: float
    reps_prescribed: int
    weight_used: Optional[float]
    reps_completed: Optional[float]

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_IN_PROG


class StrengthSetFinished(TableBase):
    """a set already finalized"""
    exercise_key: _models.strength_exercise.StrengthExerciseKey
    week: int
    day: int
    weight_prescribed: float
    reps_prescribed: int
    weight_used: float
    reps_completed: float

    @classmethod
    def get_table_name(cls) -> str:
        return _SET_FINISHED


class _SetToProgramLink(TableBase):
    program_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key=f"{_PROGRAM_TABLE_NAME}.id"
    )
    set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key=f"{_SETS_TABLE_NAME}.id"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _LINK_TABLE_NAME


class ActiveProgramRecord(TableBase):
    execution_guid: spice_rack.guid.GuidStr = Field(
        description="globally unique id for this program execution",
        default_factory=spice_rack.guid.GuidStr.generate
    )
    template_key: _ProgramTemplateKey = Field(
        description="key for the template this is an invocation of"
    )
    started_at: spice_rack.timestamp.Timestamp = Field(description="when the program started")
    updated_at: spice_rack.timestamp.Timestamp = Field(
        description="last time we executed a day of this program"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "active_programs"
