from __future__ import annotations
from typing import ClassVar, Optional
from sqlmodel import Field, Relationship

import spice_rack
from liftz import _models
from liftz._repos import _record_base


_ProgramTemplateKey = _models.program_template.components.ProgramTemplateKey
_ProgramTemplateTags = _models.program_template.components.ProgramTemplateTags

_TEMPLATE_TABLE_NAME = "program_templates"
_TEMPLATE_SET_TABLE_NAME = "individual_template_sets"


__all__ = (
    "ProgramTemplateTagsStr",
    "ProgramTemplateRecord",
    "ProgramTemplateIndividualSet"
)


class ProgramTemplateTagsStr(spice_rack.AbstractSpecialStr):
    """string of combined enum values, joined by a comma"""
    _sep: ClassVar[str] = ","

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        for part in root_data.split(cls._sep):
            _ProgramTemplateTags(part)
        return root_data

    @classmethod
    def from_tag_list(cls, tags: list[_ProgramTemplateTags]) -> str:
        member_strs = [m.value for m in tags]
        return cls(cls._sep.join(member_strs))

    def to_tag_list(self) -> list[_ProgramTemplateTags]:
        tags = []
        for part in self.split(self._sep):
            tags.append(
                _ProgramTemplateTags(part)
            )
        return tags


class ProgramTemplateIndividualSetLink(
    _record_base.TableBase
):
    @classmethod
    def get_table_name(cls) -> str:
        return "program_template_sets_link"

    program_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key=f"{_TEMPLATE_TABLE_NAME}.id"
    )
    set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key=f"{_TEMPLATE_SET_TABLE_NAME}.id"
    )


class ProgramTemplateRecord(_record_base.TableBase):
    key: _ProgramTemplateKey
    description: str = Field(description="free-form description")
    tags: Optional[ProgramTemplateTagsStr] = Field(
        description="str-representation of a list of tags"
    )
    strength_sets: list[ProgramTemplateIndividualSet] = Relationship(
        back_populates=_TEMPLATE_SET_TABLE_NAME, link_model=ProgramTemplateIndividualSetLink
    )

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_TABLE_NAME


class ProgramTemplateIndividualSet(_record_base.TableBase):
    program_key: _ProgramTemplateKey
    exercise_key: _models.strength_exercise.StrengthExerciseKey
    week: int
    day: int
    weight: float
    reps: int

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_SET_TABLE_NAME
