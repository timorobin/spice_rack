from __future__ import annotations
from pydantic import Field

import spice_rack

from liftz._models._program_template._components import (
    ProgramTemplateKey, ProgramTemplateTags, ProgramTemplateWeek
)


__all__ = (
    "ProgramTemplate",
)


class ProgramTemplate(spice_rack.pydantic_bases.AbstractValueModel):
    """
    a template for a program, which lays out a sequence of
     weeks which contain a sequence of days to perform exercises.
    """
    key: ProgramTemplateKey = Field(description="the unique key for this template")
    description: str = Field(description="free-form description")
    tags: list[ProgramTemplateTags] = Field(description="tags connected to the template")
    weeks: list[ProgramTemplateWeek] = Field(
        description="the sequence of weeks containing the prescribed exercises"
    )
