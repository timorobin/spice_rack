from __future__ import annotations
import mimetypes
import typing as t

from spice_rack import _bases


__all__ = (
    "FileExt",
    "MimeType"
)


class FileExt(_bases.special_str.SpecialStrBase):
    """formats a file ext to make working with them more convenient"""

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        if root_data.startswith("."):
            root_data = root_data[1:]
        return root_data

    def with_dot_prefix(self) -> str:
        return f".{self}"

    def __eq__(self, other: str) -> bool:
        return str(self) == str(FileExt(other))

    def get_mime_type(self) -> t.Optional[MimeType]:
        path_like = f"x.{self[1:]}"
        mime_type, content_encoding = mimetypes.guess_type(url=path_like, strict=True)
        if mime_type is None:
            return None

        else:
            return MimeType(mime_type)


_FILE_EXTENSIONS_SET = set(mimetypes.types_map.keys())
_MIME_TYPES_SET = set(mimetypes.types_map.values())


class MimeType(_bases.special_str.SpecialStrBase):
    """
    a subclass of a string representing a MIME type.
    see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
    """

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        if root_data not in _MIME_TYPES_SET:
            raise ValueError(
                f"'{root_data}' not a valid mime type. see: "
                f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types"
            )

        else:
            split = root_data.split("/")
            if len(split) != 2:
                raise ValueError(
                    f"expected mimetype to be in format <type>/<subtype>, '{root_data}' is not."
                )
            return root_data

    @property
    def type(self) -> str:
        """get the top level mimetype"""
        return self.split("/")[0]

    @property
    def subtype(self) -> str:
        """get the subtype for this mimetype"""
        return self.split("/")[-1]

    @classmethod
    def from_file_ext(cls, file_ext_or_dot_file_ext: t.Union[str, FileExt]) -> MimeType:
        """
        get the relevant mimetype for the given file extension

        Args:
            file_ext_or_dot_file_ext: a file extension, either with or without the initial '.'

        Returns: the mime type if it is found, value error if nothing found
        """
        if file_ext_or_dot_file_ext.startswith("."):
            file_ext = file_ext_or_dot_file_ext[1:]
        else:
            file_ext = file_ext_or_dot_file_ext

        # make placeholder path-like str for the stdlib lookup func.
        # https://docs.python.org/3/library/mimetypes.html#mimetypes.guess_type
        path_like = f"x.{file_ext}"
        mime_type, content_encoding = mimetypes.guess_type(url=path_like, strict=True)
        if mime_type is None:
            raise ValueError(
                f"failed to find mimetype for file ext: '{file_ext_or_dot_file_ext}'"
            )
        else:
            return MimeType(mime_type)

    def get_possible_file_extensions(self) -> list[FileExt]:
        """return the list of file extensions for this file mimetype"""
        res = []
        for file_ext, mime_type in mimetypes.types_map.items():
            if mime_type == str(self):
                res.append(FileExt(file_ext))
        return res
