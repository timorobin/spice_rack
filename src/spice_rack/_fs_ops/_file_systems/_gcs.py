from __future__ import annotations
from typing import final, Union, Literal, Iterator
import gcsfs  # noqa
from pydantic import Field

from spice_rack._fs_ops import _path_strs, _helpers
from spice_rack._fs_ops._file_systems import _base
from spice_rack import _gcp_auth


__all__ = (
    "GcsFileSystem",
)


@final
class GcsFileSystem(_base.AbstractFileSystem, class_id="gcs"):
    """wrapper for the GCSFileSystem file system"""
    creds: _gcp_auth.AnyGcpAuthStrat = Field(
        description="the credentials we use to authenticate to the gcs bucket",
        default_factory=_gcp_auth.AnyGcpAuthStrat.init_default
    )

    @classmethod
    def get_fs_specific_prefix(cls) -> str:
        return "gs://"

    def _get_gcsfs_token(
            self,
    ) -> Union[str, dict]:
        creds: _gcp_auth.auth_strategies.AbstractGcpAuthStrategy = self.creds.root

        if isinstance(creds, _gcp_auth.auth_strategies.AnonAuthStrategy):
            return "anon"
        elif isinstance(creds, _gcp_auth.auth_strategies.DefaultAuthStrategy):
            return "google_default"
        elif isinstance(creds, _gcp_auth.auth_strategies.ServiceAcctKeyFileAuthStrategy):
            return creds.file_path
        elif isinstance(creds, _gcp_auth.auth_strategies.ServiceAcctKeyAuthStrategy):
            return creds.key_data.dict(exclude_defaults=True)
        else:
            raise ValueError(f"unexpected auth strategy type: {type(self.creds,)}")

    def build_fsspec_file_system(self) -> gcsfs.GCSFileSystem:
        token = self._get_gcsfs_token()
        return gcsfs.GCSFileSystem(
            token=token
        )

    def make_dir(
            self,
            path: _path_strs.AbsoluteDirPathStr,
            if_exists: Literal["raise", "return"] = "return",
            create_parents: bool = True
    ) -> None:

        # creating cloud dir doesn't work like local bc how
        # they treat directories. We create a placeholder
        # file when making a directory to imitate this.
        super().make_dir(path=path, if_exists=if_exists, create_parents=create_parents)
        if not self.exists(path):
            placeholder_path = path.joinpath(rel_path=_helpers.get_placeholder_rel_path())
            with self.open_file(placeholder_path, "wb") as f:
                f.write("placeholder text".encode())

    def iter_dir_contents(
            self,
            path: _path_strs.AbsoluteDirPathStr,
    ) -> Iterator[_path_strs.FileOrDirAbsPathT]:
        for path_i in super().iter_dir_contents(path=path):
            if _helpers.is_placeholder_file_path(path_i):
                continue
            else:
                yield path_i

    def get_home_dir(self) -> _path_strs.AbsoluteDirPathStr:
        return _path_strs.AbsoluteDirPathStr("/")
