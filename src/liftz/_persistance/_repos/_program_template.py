from __future__ import annotations
import typing as t
from sqlalchemy import orm

from liftz import _models
from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    ProgramTemplateKeyT,
    StrengthExerciseKeyT,
    ProgramTemplateTagsT,
    UserIdT
)

_TEMPLATE_TABLE_NAME = "program_templates"
_TEMPLATE_SET_TABLE_NAME = "individual_template_sets"


__all__ = (
    "ProgramTemplateRecord",
    "ProgramTemplateIndividualSet"
)


class ProgramTemplateRecord(_record_base.TableBase):
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True,
    )
    key: orm.Mapped[ProgramTemplateKeyT] = orm.mapped_column(
        doc="the key of the program template", unique=True
    )
    description: orm.Mapped[str] = orm.mapped_column(doc="free-form description")
    tags: orm.Mapped[list[ProgramTemplateTagsT]] = orm.mapped_column(
        doc="a list of tags tied to this program"
    )
    strength_sets: orm.Mapped[list[ProgramTemplateIndividualSet]] = orm.relationship(
        cascade="all, delete-orphan",
        back_populates="program_template_record"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_TABLE_NAME


class ProgramTemplateIndividualSet(_record_base.TableBase):
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="the id of the user connected to this record",
        index=True,
    )
    program_template_record: orm.Mapped[ProgramTemplateRecord] = orm.relationship(
        back_populates="strength_sets"
    )
    exercise_key: orm.Mapped[StrengthExerciseKeyT] = orm.mapped_column(
        doc="key to the exercise"
    )
    week: orm.Mapped[int] = orm.mapped_column(
        doc="the week this set is from"
    )
    day: orm.Mapped[int] = orm.mapped_column(
        doc="the day within the week"
    )
    weight: orm.Mapped[float] = orm.mapped_column(
        doc="the weight prescribed"
    )
    reps: orm.Mapped[int] = orm.mapped_column(
        doc="the reps prescribed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_SET_TABLE_NAME
