from __future__ import annotations
from pydantic import Field
from typing import Optional

import spice_rack
from liftz._persistance._repos._record_base import TableBase
from liftz import _models

_ProgramTemplateKey = _models.program_template.components.ProgramTemplateKey
_ProgramTemplateTags = _models.program_template.components.ProgramTemplateTags

__all__ = (
    "FinalizedStrengthSet",
    "FinalizedProgramRunRecord"
)

_SETS_TABLE_NAME = "finalized_strength_sets"
_PROGRAM_TABLE_NAME = "finalized_program_run"
_LINK_TABLE_NAME = "finalized_strength_sets_to_program_record"


class FinalizedStrengthSet(TableBase):
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
        return _SETS_TABLE_NAME


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


class FinalizedProgramRunRecord(TableBase):
    execution_guid: spice_rack.guid.GuidStr = Field(
        description="globally unique id for this program execution",
        default_factory=spice_rack.guid.GuidStr.generate
    )
    template_key: _ProgramTemplateKey = Field(
        description="key for the template this is an invocation of"
    )
    started_at: spice_rack.timestamp.Timestamp = Field(description="when the program started")
    finished_at: spice_rack.timestamp.Timestamp = Field(
        description="the timestamp when this program execution was finalized"
    )
    strength_sets: list[FinalizedStrengthSet] = Relationship(
        back_populates=_SETS_TABLE_NAME, link_model=_SetToProgramLink
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _PROGRAM_TABLE_NAME
