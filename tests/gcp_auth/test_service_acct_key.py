import pytest
from gcsfs import GCSFileSystem


from spice_rack import _gcp_auth


@pytest.fixture(scope="module")
def auth_strat_inst(
        service_account_key_data
) -> _gcp_auth.auth_strategies.ServiceAcctKeyAuthStrategy:
    return _gcp_auth.auth_strategies.ServiceAcctKeyAuthStrategy(
        key_data=service_account_key_data  # noqa should parse
    )


def test_building_creds(auth_strat_inst):
    from google.auth import credentials
    creds = auth_strat_inst.build_gcp_creds()
    assert isinstance(creds, credentials.Credentials)


def test_public_bucket(auth_strat_inst, public_bucket):
    token = auth_strat_inst.key_data.model_dump(exclude_defaults=True)
    fs = GCSFileSystem(token=token)
    assert fs.exists(path=public_bucket)


def test_protected_bucket(auth_strat_inst, protected_bucket):
    token = auth_strat_inst.key_data.model_dump(exclude_defaults=True)
    fs = GCSFileSystem(token=token)
    assert fs.exists(protected_bucket)
