======
fs_ops
======
This package contains classes and related functionality for working with file and directories,
on different underlying file systems. The main idea is to standardize the interface for interacting
with file systems, regardless of if it is local, s3, gcs, or sftp etc.
Right now we only support local, gcs, and sftp, but s3 soon.


File System Models
------------------
Top level classes that we interact with.

.. autopydantic_model:: spice_rack._fs_ops._fs_models.FilePath
   :members:

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DirPath
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirPathT
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirPathTypeAdapter
   :members:

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DeferredFilePath
   :members:

.. autopydantic_model:: spice_rack._fs_ops._fs_models.DeferredDirPath
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirDeferredPathT
   :members:

.. autoclass:: spice_rack._fs_ops._fs_models.FileOrDirDeferredPathTypeAdapter
   :members:
