from spice_rack._fs_ops._file_systems._base import *
from spice_rack._fs_ops._file_systems._local import *
from spice_rack._fs_ops._file_systems._gcs import *
from spice_rack._fs_ops._file_systems._sftp import *
from spice_rack._fs_ops._file_systems._sftp import *
from spice_rack._fs_ops._file_systems._fs_inference import *

AnyFileSystemT = AbstractFileSystem.build_dispatched_ann()
AnyFileSystemTypeAdapter = AbstractFileSystem.build_dispatcher_type_adapter()
