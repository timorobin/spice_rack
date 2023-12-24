from __future__ import annotations

from spice_rack import base_classes, guid


class ProgramTemplateTask(base_classes.pydantic.AbstractValueModel):
    ...


class ProgramTemplateDay(base_classes.pydantic.AbstractValueModel):
    tasks: list[ProgramTemplateTask]


class ProgramTemplateWeek(base_classes.pydantic.AbstractValueModel):
    days: list[ProgramTemplateDay]


class ProgramTemplateEntity(base_classes.pydantic.AbstractValueModel, guid.GuidMixin):
    """entity for a program template entity"""
    weeks: list[ProgramTemplateWeek]
