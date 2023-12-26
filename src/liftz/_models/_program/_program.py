from __future__ import annotations
from typing import Optional
from pydantic import Field

import spice_rack
from liftz._models import _program_template
from liftz._models._program import _components


__all__ = (
    "ActiveProgram",
    "FinishedProgram"
)


class ActiveProgram(spice_rack.pydantic_bases.AbstractValueModel):
    """
    current program the user is working through. The specific day records are all generated at
    start-time. When a day is started, we remove an item from the days_left field,
    populate the in-progress day record, then when it is finished,
    we empty the 'in_progress' attr and create a new days_finished item.
    """
    execution_guid: spice_rack.guid.GuidStr = Field(
        description="globally unique id for this program execution",
        default_factory=spice_rack.guid.GuidStr.generate
    )
    template_key: _program_template.components.ProgramTemplateKey = Field(
        description="key for the template this is an invocation of"
    )
    started_at: spice_rack.timestamp.Timestamp = Field(description="when the program started")
    updated_at: spice_rack.timestamp.Timestamp = Field(
        description="last time we executed a day of this program"
    )
    days_finished: list[_components.ProgramDayFinished] = Field(
        description="days we've completed"
    )
    days_left: list[_components.ProgramDayNotStarted] = Field(
        description="days we haven't started"
    )
    in_progress_day: Optional[_components.ProgramDayInProgress] = Field(
        description="a day we have in progress if we have one in progress"
    )


class FinishedProgram(spice_rack.pydantic_bases.AbstractValueModel):
    """
    finalized record of a program the user is done working through. These can no longer be updated
    in the database
    """
    execution_guid: spice_rack.guid.GuidStr = Field(
        description="globally unique id for this program execution",
    )
    template_key: _program_template.components.ProgramTemplateKey = Field(
        description="key for the template this is an invocation of"
    )
    started_at: spice_rack.timestamp.Timestamp = Field(description="when the program started")
    finished_at: spice_rack.timestamp.Timestamp = Field(
        description="timestamp when we finished this program"
    )
    days_finished: list[_components.ProgramDayFinished] = Field(
        description="days we've completed"
    )
