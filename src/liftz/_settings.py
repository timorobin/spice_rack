from __future__ import annotations
import typing as t
from pathlib import Path

from pydantic import Field

import spice_rack

if t.TYPE_CHECKING:
    from liftz import _models


__all__ = (
    "Settings",
)


def _get_default_exercises() -> list[_models.strength_exercise.StrengthExerciseDef]:
    from liftz import _models
    return [
        _models.strength_exercise.StrengthExerciseDef(
            key=_models.strength_exercise.StrengthExerciseKey("squat"),
            description="basic barbell squat",
            tags=[_models.strength_exercise.StrengthExerciseTags.LOWER]
        ),
        _models.strength_exercise.StrengthExerciseDef(
            key=_models.strength_exercise.StrengthExerciseKey("deadlift"),
            description="basic barbell deadlift",
            tags=[_models.strength_exercise.StrengthExerciseTags.LOWER]
        ),
        _models.strength_exercise.StrengthExerciseDef(
            key=_models.strength_exercise.StrengthExerciseKey("bench"),
            description="basic barbell bench press",
            tags=[_models.strength_exercise.StrengthExerciseTags.LOWER]
        ),
        _models.strength_exercise.StrengthExerciseDef(
            key=_models.strength_exercise.StrengthExerciseKey("ohp"),
            description="basic barbell over-head press",
            tags=[_models.strength_exercise.StrengthExerciseTags.LOWER]
        )
    ]


class Settings(spice_rack.AbstractSettings):
    """settings for the app"""
    db_uri: str = Field(
        description="the uri to the db, default is in-mem sqlite", default="sqlite://"
    )
    system_strength_exercises: list[_models.strength_exercise.StrengthExerciseDef] = Field(
        description="list of exercises to add on startup",
        default_factory=_get_default_exercises
    )

    @classmethod
    def update_forward_refs(cls, **kwargs) -> None:
        from liftz import _models
        kwargs["_models"] = _models
        return super().update_forward_refs(**kwargs)

    @classmethod
    def get_dot_env_files(cls) -> list[t.Union[str, Path]]:
        # top level of the repo folder

        dotenv_name = "liftz.env"  # for now
        # dotenv_name = ".env"

        repo_path = Path(__file__).parent.parent.parent
        return [
            repo_path.joinpath(dotenv_name),
            repo_path.parent.joinpath(dotenv_name)
        ]
