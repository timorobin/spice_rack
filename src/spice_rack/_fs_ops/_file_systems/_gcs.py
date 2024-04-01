from __future__ import annotations
import typing as t
import gcsfs  # noqa
import pydantic

from spice_rack._fs_ops import _path_strs, _helpers
from spice_rack._fs_ops._file_systems import _base
from spice_rack import _gcp_auth


__all__ = (
    "GcsFileSystem",
)


@t.final
class GcsFileSystem(_base.AbstractFileSystem, class_id="gcs"):
    """wrapper for the GCSFileSystem file system"""
    creds: _gcp_auth.AnyGcpAuthStrat = pydantic.Field(
        description="the credentials we use to authenticate to the gcs bucket",
        default_factory=_gcp_auth.AnyGcpAuthStrat.init_default
    )

    @classmethod
    def get_fs_specific_prefix(cls) -> str:
        return "gs://"

    def _get_gcsfs_token(
            self,
    ) -> t.Union[str, dict]:
        creds: _gcp_auth.auth_strategies.AbstractGcpAuthStrategy = self.creds.root

        if isinstance(creds, _gcp_auth.auth_strategies.AnonAuthStrategy):
            return "anon"

        elif isinstance(creds, _gcp_auth.auth_strategies.DefaultAuthStrategy):
            if creds.default_creds_found():
                return "google_default"
            else:
                if creds.on_no_default == "use_anon":
                    return "anon"
                elif creds.on_no_default == "raise":
                    raise ValueError(
                        "no default gcp credentials found in the environment"
                    )
                else:
                    raise ValueError(
                        f"'{creds.on_no_default}' is unexpected value for 'on_no_default'"
                    )
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

    @pydantic.validate_call
    def make_dir(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
            *,
            if_exists: t.Literal["raise", "return"] = "return",
            create_parents: bool = True
    ) -> None:

        # creating cloud dir doesn't work like local bc how
        # they treat directories. We create a placeholder
        # file when making a directory to imitate this.
        super().make_dir(__path, if_exists=if_exists, create_parents=create_parents)
        if not self.exists(__path):
            placeholder_path = __path.joinpath(rel_path=_helpers.get_placeholder_rel_path())
            with self.open_file(placeholder_path, "wb") as f:
                f.write("placeholder text".encode())

    @pydantic.validate_call
    def iter_dir_contents(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
    ) -> t.Iterator[_path_strs.FileOrDirAbsPathT]:
        """
        same iter as base class, except we also skip the file if it is the placeholder file
        """
        for path_i in super().iter_dir_contents(__path):
            if _helpers.is_placeholder_file_path(path_i):
                continue
            else:
                yield path_i

    def get_home_dir(self) -> _path_strs.AbsoluteDirPathStr:
        return _path_strs.AbsoluteDirPathStr("/")
