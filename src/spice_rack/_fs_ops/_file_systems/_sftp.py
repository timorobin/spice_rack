from __future__ import annotations
import typing as t
from pydantic import Field, validate_call
from fsspec.implementations import sftp
from paramiko.sftp_file import SFTPFile as ParamikoSftpFile
from paramiko.sftp_client import SFTPClient as ParamikoSftpClient

from spice_rack._fs_ops import _path_strs
from spice_rack._fs_ops._file_systems import _base


__all__ = (
    "SftpFileSystem",
)


@t.final
class SftpFileSystem(_base.AbstractFileSystem, class_id="sftp"):
    """wrapper for a paramiko-based sftp file system"""

    host: str = Field(description="the host url of this server")
    username: t.Optional[str] = Field(description="the username to use", default=None)
    password: t.Optional[str] = Field(description="the password to use", default=None)
    port: t.Optional[int] = Field(description="the port to use", default=None)

    @classmethod
    def get_fs_specific_prefix(cls) -> str:
        return "/"

    def build_fsspec_file_system(self) -> sftp.SFTPFileSystem:
        kwargs = {
            "host": self.host
        }
        if self.username:
            kwargs["username"] = self.username

        if self.password:
            kwargs["password"] = self.password

        if self.port:
            kwargs["port"] = self.port

        fs = sftp.SFTPFileSystem(
            **kwargs,

            # missing_host_key_policy=AutoAddPolicy()

        )
        # hacky thing to make sure it isn't closed
        if fs.ftp.sock.closed():
            fs._connect()  # noqa

        return fs

    def get_home_dir(self) -> _path_strs.AbsoluteDirPathStr:
        # todo: revisit this
        return _path_strs.AbsoluteDirPathStr("/")

    def download_file_locally(
            self,
            path: _path_strs.AbsoluteFilePathStr,
            dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteFilePathStr:
        from spice_rack._fs_ops._file_systems import _local
        local_fs = _local.LocalFileSystem()
        local_fs.make_dir(dest_dir, if_exists="return", create_parents=True)

        local_path = dest_dir.joinpath(
            _path_strs.RelFilePathStr(path.get_name(include_suffixes=True))
        )

        fsspec_inst = self.build_fsspec_file_system()
        paramiko_client: ParamikoSftpClient = fsspec_inst.ftp

        _paramiko_sftp_get(
            sftp_client=paramiko_client,
            sftp_file=self.contextualize_abs_path(path),
            local_file=str(local_path),
        )
        return local_path

    @validate_call
    def download_dir_locally(
            self,
            __source_dir: _path_strs.AbsoluteDirPathStr,
            __local_dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteDirPathStr:
        from spice_rack._fs_ops._file_systems import _local
        local_fs = _local.LocalFileSystem()
        local_fs.make_dir(__source_dir, if_exists="return", create_parents=True)

        local_path = __local_dest_dir.joinpath(
            _path_strs.RelDirPathStr(__source_dir.get_name())
        )

        for source_abs_file_path in self.iter_dir_contents_files_only(
                __source_dir, recursive=True
        ):
            rel_file_path = _path_strs.RelFilePathStr(
                str(source_abs_file_path).replace(str(__source_dir), "")
            )
            dest_abs_file_path = local_path.joinpath(rel_file_path)
            self.download_file_locally(
                path=source_abs_file_path, dest_dir=dest_abs_file_path.get_parent()
            )
        return local_path


# copied from here: https://github.com/paramiko/paramiko/issues/151#issuecomment-1076144423
# read through issue for full context, but tldr: paramiko fails on large files


def _paramiko_sftp_get(
        sftp_client: ParamikoSftpClient,
        sftp_file: str,
        local_file: str,
        callback: t.Optional[t.Callable[[int, int], None]] = None,
        max_request_size: int = 2 ** 28) -> int:
    """
    A copy of paramiko's sftp.get() function that allows for sequential download
    of large chunks.
    This is a work-around for https://github.com/paramiko/paramiko/issues/151.
    The issue does not occur when prefetch=False (i.e. sequential download) indicating
    that there seems to be an error with the parallel approach. However, the sequential
    version in paramiko does not allow customizable request size, and instead hardcodes a
    small value that is known to work with many SFTP implementations.
    With the possibility of large chunks, the sequential download's RTT overhead becomes
    less of a pain and a viable alternative.
    :param sftp_client: Paramiko's SFTPClient.
    :param sftp_file: The remote file in sftp.
    :param local_file: The local file.
    :param callback: A function that is invoked on every chunk.
    :param max_request_size: The max request size, defaults to 2**20.
    :return: The size of the file in bytes.
    """

    with open(local_file, "wb") as local_handle:
        file_size = sftp_client.stat(sftp_file).st_size
        assert file_size is not None

        with sftp_client.open(sftp_file, "rb") as remove_handle:
            _paramiko_transfer_with_callback(
                remove_handle,
                local_handle,
                file_size,
                callback,
                max_request_size
            )

    return file_size


def _paramiko_transfer_with_callback(
        reader: ParamikoSftpFile,
        writer: "BinaryIO",  # noqa 821 -- not sure where this comes from
        file_size: int,
        callback: t.Optional[t.Callable[[int, int], None]],
        max_request_size: int):
    """
    A copy of paramiko's sftp_client._transfer_with_callback with max_request_size support.
    :param reader: The reader file handle.
    :param writer: The writer file handle.
    :param file_size: The size of the file to be downloaded.
    :param callback: A function that is invoked on every chunk.
    :param max_request_size: The max request size, defaults to 2**20.
    """
    size = 0
    reader.MAX_REQUEST_SIZE = max_request_size

    while True:
        remaining = file_size - size
        chunk = min(max_request_size, remaining)

        data = reader.read(chunk)
        writer.write(data)
        size += len(data)

        if len(data) == 0:
            break

        if callback is not None:
            callback(size, file_size)

    assert size == file_size
