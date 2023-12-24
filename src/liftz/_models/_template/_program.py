from __future__ import annotations

from spice_rack import base_classes
from liftz._models._template._exercise import DayTemplateExerciseItem
from liftz._models._record_mixin import RecordMixin, RecordRef


__all__ = (
    "ProgramTemplateDay",
    "ProgramTemplateKey",
    "ProgramTemplateEntity",
    "ProgramTemplateRecord",
    "ProgramTemplateDayExerciseRecord"
)


class ProgramTemplateDay(base_classes.pydantic.AbstractValueModel):
    week: int
    day: int
    exercises: list[DayTemplateExerciseItem]


class ProgramTemplateKey(base_classes.AbstractSpecialStr):

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data


class _ProgramTemplateCommon(
    base_classes.pydantic.AbstractValueModel,
):
    key: ProgramTemplateKey


class ProgramTemplateEntity(
    _ProgramTemplateCommon,
):
    """entity for a program template entity"""
    days: list[ProgramTemplateDay]


class ProgramTemplateRecord(_ProgramTemplateCommon, RecordMixin):

    @classmethod
    def get_repo_name(cls) -> str:
        return "program_templates"


class ProgramTemplateDayExerciseRecord(RecordMixin):
    program_template_ref: RecordRef[ProgramTemplateRecord]

    @classmethod
    def get_repo_name(cls) -> str:
        return "program_template_exercises"

