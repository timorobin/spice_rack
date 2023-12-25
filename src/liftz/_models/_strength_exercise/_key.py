from __future__ import annotations

from spice_rack import base_classes


__all__ = (
    "StrengthExerciseKey",
)


class StrengthExerciseKey(base_classes.AbstractSpecialStr):
    """special string for a strength exercise"""
    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data
