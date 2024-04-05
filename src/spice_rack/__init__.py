from spice_rack import (
    _bases as bases,
    _logging as logging,
    _fs_ops as fs_ops,
    _gcp_auth as gcp_auth,
    _ts_service as ts_service,
    _misc as misc,
    _utils as utils,
    _guid_service as guid_service,
    _frozen_registry as frozen_registry,
    _polars_service as polars_service,
    _version_getter
)
GuidT = guid_service.GuidT
Logger = logging.Logger


__version__ = _version_getter.get_version(__name__)
VERSION = __version__
