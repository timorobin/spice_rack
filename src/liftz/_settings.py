from __future__ import annotations
import typing as t
from pathlib import Path
from pydantic import Field

import spice_rack


__all__ = (
    "Settings",
)


class Settings(spice_rack.AbstractSettings):
    """settings for the app"""
    db_uri: str = Field(
        description="the uri to the db, default is in-mem sqlite", default="sqlite://"
    )

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
