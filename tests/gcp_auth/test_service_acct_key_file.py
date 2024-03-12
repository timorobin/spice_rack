import pytest
from pathlib import Path
import json
from gcsfs import GCSFileSystem

from spice_rack import _gcp_auth


@pytest.fixture(scope="module")
def service_acct_key_fp(service_account_key_data) -> str:
    fp_obj = Path(__file__).parent.joinpath("gcs_key.json")
    with open(fp_obj, "w+") as f:
        json.dump(service_account_key_data, f)
    yield str(fp_obj)
    fp_obj.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def auth_strat_inst(
        service_acct_key_fp
) -> _gcp_auth.auth_strategies.ServiceAcctKeyFileAuthStrategy:
    return _gcp_auth.auth_strategies.ServiceAcctKeyFileAuthStrategy(file_path=service_acct_key_fp)


def test_building_creds(auth_strat_inst):
    from google.auth import credentials
    creds = auth_strat_inst.build_gcp_creds()
    assert isinstance(creds, credentials.Credentials)


def test_public_bucket(auth_strat_inst, public_bucket):
    token = auth_strat_inst.file_path
    fs = GCSFileSystem(token=token)
    assert fs.exists(path=public_bucket)


def test_protected_bucket(auth_strat_inst, protected_bucket):
    token = auth_strat_inst.file_path
    fs = GCSFileSystem(token=token)
    assert fs.exists(protected_bucket)
