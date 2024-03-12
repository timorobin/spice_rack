from __future__ import annotations as _annotations

# import all file system modules here
from fs_ops._file_systems.base import *
from fs_ops._file_systems.local import *
from fs_ops._file_systems.gcs import *
from fs_ops._file_systems.s3 import *
from fs_ops._file_systems.sftp import *


from strlt_common.type_ann_builder.dispatched_cls_type_ann_builder \
    import build_concrete_union_type_ann as _type_builder


AnyFileSystemTypeAnn = _type_builder(
    root_cls=AbstractFileSystem
)
