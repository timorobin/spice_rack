from __future__ import annotations
from typing import Optional
from pydantic import Field

import spice_rack
from liftz._models import _program_template
from liftz._models._program_in_progress import _components


class ActiveProgram(spice_rack.pydantic_bases.AbstractValueModel):
    template_key: _program_template.components.ProgramTemplateKey = Field(
        description="key for the template this is an invocation of"
    )
    started_at: spice_rack.timestamp.Timestamp = Field(description="when the program started")
    updated_at: spice_rack.timestamp.Timestamp = Field(
        description="last time we executed a day of this program"
    )
    days_finished: list[_components.ProgramDayFinished]
    days_left: list[_components.ProgramDayNotStarted]
    in_progress_day: Optional[_components.ProgramDayInProgress] = None
    