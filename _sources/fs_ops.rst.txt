======
fs_ops
======
This package contains classes and related functionality for working with file and directories,
on different underlying file systems. The main idea is to standardize the interface for interacting
with file systems, regardless of if it is local, s3, gcs, or sftp etc.
Right now we only support local, gcs, and sftp, but s3 soon.


Path Objects
------------
Top level classes that we interact with.

.. autopydantic_model:: spice_rack._fs_ops._fs_models.FilePath
   :members:
   :model-show-json: False
   :inherited-members: BaseModel

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DirPath
   :members:
   :model-show-json: False
   :inherited-members: BaseModel

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirPathT
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirPathTypeAdapter
   :members:

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DeferredFilePath
   :members:
   :model-show-json: False
   :inherited-members: BaseModel

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DeferredDirPath
   :members:
   :model-show-json: False
   :inherited-members: BaseModel

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirDeferredPathT
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirDeferredPathTypeAdapter
   :members:


File Systems
------------
The file system-specific implementations of the interface.
Instances of these classes live on FilePath and DirPath instances.

.. autopydantic_model:: spice_rack._fs_ops._file_systems.AbstractFileSystem
   :members:
   :inherited-members: PydanticBase
   :model-show-json: False

.. autopydantic_model:: spice_rack._fs_ops._file_systems.LocalFileSystem
   :members:
   :inherited-members: PydanticBase
   :model-show-json: False

.. autopydantic_model:: spice_rack._fs_ops._file_systems.SftpFileSystem
   :members:
   :inherited-members: PydanticBase
   :model-show-json: False

.. autopydantic_model:: spice_rack._fs_ops._file_systems.GcsFileSystem
   :members:
   :inherited-members: PydanticBase
   :model-show-json: False
