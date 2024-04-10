import pytest
from gcsfs import GCSFileSystem
from google.auth import credentials

from spice_rack import gcp_auth


def test_building_creds():

    # check that if we fail to build default creds, we default to anonymous ones.
    try:
        strat = gcp_auth.auth_strategies.DefaultAuthStrategy(on_no_default="raise")
        strat.build_gcp_creds()
        default_failed = False
    except gcp_auth.exceptions.DefaultAuthNotAvailableException:
        default_failed = True
    except Exception as e:
        raise pytest.fail(str(e))

    strat = gcp_auth.auth_strategies.DefaultAuthStrategy(on_no_default="use_anon")
    creds = strat.build_gcp_creds()

    if default_failed:
        assert isinstance(creds, credentials.AnonymousCredentials)
    else:
        assert not isinstance(creds, credentials.AnonymousCredentials)


def test_public_bucket(public_bucket):
    strat = gcp_auth.auth_strategies.DefaultAuthStrategy(on_no_default="use_anon")
    creds = strat.build_gcp_creds()

    # specifically
    if isinstance(creds, credentials.AnonymousCredentials):
        token = "anon"
    else:
        token = "google_default"

    fs = GCSFileSystem(token=token)
    assert fs.exists(path=public_bucket)


def test_protected_bucket(protected_bucket):
    strat = gcp_auth.auth_strategies.DefaultAuthStrategy(on_no_default="use_anon")
    creds = strat.build_gcp_creds()

    # specifically
    if isinstance(creds, credentials.AnonymousCredentials):
        pytest.skip("default creds not set. cannot test on private bucket")
    else:
        token = "google_default"

        fs = GCSFileSystem(token=token)
        try:
            assert fs.exists(protected_bucket)
        except OSError:  # this happens when we run this test in github action. it is ok
            pass

        except Exception as e:
            pytest.fail(f"'exists' call failed. error {e}")
