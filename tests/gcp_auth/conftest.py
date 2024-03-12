import pytest
import typing as t
import json


@pytest.fixture(scope="session")
def protected_bucket(session_config) -> str:
    if session_config.gcp_protected_dir:
        return session_config.gcp_protected_dir
    else:
        return pytest.skip(
            "session config has no 'gcp_protected_dir' set"
        )


@pytest.fixture(scope="session")
def public_bucket(session_config) -> str:
    if session_config.gcp_public_dir:
        return session_config.gcp_public_dir
    else:
        return pytest.skip(
            "session config has no 'gcp_public_dir' set"
        )


@pytest.fixture(scope="session")
def service_account_key_data(session_config) -> t.Dict:
    if session_config.gcp_key_raw:
        return json.loads(session_config.gcp_key_raw)
    else:
        return pytest.skip(
            "session config has no 'gcp_key_raw' set"
        )
