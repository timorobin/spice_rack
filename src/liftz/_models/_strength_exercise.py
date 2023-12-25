from __future__ import annotations
from pydantic import Field

import spice_rack


__all__ = (
    "StrengthExerciseKey",
    "StrengthExerciseTags",
    "StrengthExerciseDef",
)


class StrengthExerciseKey(spice_rack.AbstractSpecialStr):
    """special string for a strength exercise"""
    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data


class StrengthExerciseTags(spice_rack.enum_bases.StrEnum):
    """tags available for a strength exercise"""
    UPPER = "upper"
    LOWER = "lower"


class StrengthExerciseDef(
    spice_rack.pydantic_bases.AbstractValueModel
):
    """
    internal representation of a strength exercise definition.
    A strength exercise definition establishes a potential exercise we can choose in a program
    """
    key: StrengthExerciseKey = Field(
        description="the key for this exercise, unique across all strength exercises"
    )
    description: str = Field(description="the free-form text description")
    tags: list[StrengthExerciseTags] = Field(description="tags for the exercise")
