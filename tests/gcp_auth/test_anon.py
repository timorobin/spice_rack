import pytest

from gcsfs import GCSFileSystem
from gcsfs.retry import HttpError


from spice_rack import _gcp_auth


@pytest.fixture(scope="module")
def auth_strat_inst() -> _gcp_auth.auth_strategies.AnonAuthStrategy:
    return _gcp_auth.auth_strategies.AnonAuthStrategy()


def test_building_creds(auth_strat_inst):
    from google.auth import credentials
    creds = auth_strat_inst.build_gcp_creds()
    assert isinstance(creds, credentials.Credentials)


def test_public_bucket(auth_strat_inst, public_bucket):
    token = "anon"
    fs = GCSFileSystem(token=token)
    assert fs.exists(path=public_bucket)


def test_protected_bucket(auth_strat_inst, protected_bucket):
    token = "anon"
    fs = GCSFileSystem(token=token)
    with pytest.raises(HttpError):
        fs.exists(protected_bucket)
