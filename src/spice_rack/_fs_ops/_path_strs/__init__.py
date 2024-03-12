import typing as _t

from spice_rack._fs_ops._path_strs._base import *
from spice_rack._fs_ops._path_strs._abs import *
from spice_rack._fs_ops._path_strs._rel import *

RelOrAbsFilePathT = _t.Union[AbsoluteFilePathStr, RelFilePathStr]
RelOrAbsDirPathT = _t.Union[AbsoluteDirPathStr, RelDirPathStr]
