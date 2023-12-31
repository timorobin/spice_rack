from __future__ import annotations
from sqlmodel import Field, Relationship

from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    ProgramTemplateKeyT,
    StrengthExerciseKeyT,
    # ProgramTemplateTagsT,
    UserIdT
)

_TEMPLATE_TABLE_NAME = "program_templates"
_TEMPLATE_SET_TABLE_NAME = "individual_template_sets"


__all__ = (
    "ProgramTemplateRecord",
    "ProgramTemplateIndividualSet"
)


class ProgramTemplateRecord(_record_base.TableBase):
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True,
    )
    key: ProgramTemplateKeyT = Field(
        description="the key of the program template", unique=True
    )
    description: str = Field(description="free-form description")
    # tags: orm.Mapped[list[ProgramTemplateTagsT]] = Field(
    #     ARRAY(Enum),
    #     description="a list of tags tied to this program"
    # )
    strength_sets: list[ProgramTemplateIndividualSet] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_TABLE_NAME


class ProgramTemplateIndividualSet(_record_base.TableBase):
    user_id: UserIdT = Field(
        description="the id of the user connected to this record",
        index=True,
    )
    program_record_id: int = Field(foreign_key=f"{_TEMPLATE_TABLE_NAME}.id")
    exercise_key: StrengthExerciseKeyT = Field(
        description="key to the exercise"
    )
    week: int = Field(
        description="the week this set is from"
    )
    day: int = Field(
        description="the day within the week"
    )
    weight: float = Field(
        description="the weight prescribed"
    )
    reps: int = Field(
        description="the reps prescribed"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_SET_TABLE_NAME
