from __future__ import annotations
import typing as t
from pathlib import Path
import pydantic

from spice_rack import bases


__all__ = (
    "TestConfig",
)


class TestConfig(bases.settings.SettingsBase):
    """
    configurable values we can load from the environment or a .env file.
    use this to pass in secrets.

    should be able to init with defaults only, and if value is missing, skip the test
    """
    gcp_key_raw: t.Optional[str] = pydantic.Field(
        description="raw json string for gcp service account key",
        default=None
    )
    gcp_public_dir: t.Optional[str] = pydantic.Field(
        description="public gcs directory used in testing",
        default=None
    )
    gcp_protected_dir: t.Optional[str] = pydantic.Field(
        description="private gcs directory used in testing",
        default=None
    )

    @classmethod
    def _get_dot_env_files(cls) -> list[Path]:
        """
        return relative or absolute file paths to .env files in descending precedence, so last
        one specified will be the highest precedence.
        """
        return [
            Path(__file__).parent.joinpath(".env")
        ]
