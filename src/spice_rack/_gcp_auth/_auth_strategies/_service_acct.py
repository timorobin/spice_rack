from __future__ import annotations
import typing as t
import pydantic
from google.auth.credentials import Credentials  # noqa
from google.oauth2 import service_account  # noqa

from spice_rack._gcp_auth._auth_strategies import _base
from spice_rack import _bases


__all__ = (
    "ServiceAcctKeyFileAuthStrategy",
    "GcpServiceAccountKeyData",
    "ServiceAcctKeyAuthStrategy"
)


class ServiceAcctKeyFileAuthStrategy(_base.AbstractGcpAuthStrategy):
    """
    see `docs <https://googleapis.dev/python/google-api-core/latest/auth.html#authentication>`_
    """
    file_path: str = pydantic.Field(
        description="the raw string to a given file that holds the creds"
    )

    def build_gcp_creds(self) -> Credentials:
        return service_account.Credentials.from_service_account_file(
            filename=self.file_path
        )


class GcpServiceAccountKeyData(_bases.value_model.ValueModelBase):
    """data from a gcp service account's json key"""
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: t.Optional[str] = None
    refresh_token: t.Optional[str] = None
    client_secret: t.Optional[str] = None

    @pydantic.field_validator("private_key", mode="before")
    def _remove_double_new_lines(cls, v: str):
        # this happens when we json encode this object sometimes IDK why
        v = v.replace("\\n", "\n")
        return v


class ServiceAcctKeyAuthStrategy(_base.AbstractGcpAuthStrategy):
    """
    see `docs <https://googleapis.dev/python/google-api-core/latest/auth.html#authentication>`_
    """
    key_data: GcpServiceAccountKeyData = pydantic.Field(
        description="the actual json contents of the key",
    )

    def build_gcp_creds(self) -> Credentials:
        return service_account.Credentials.from_service_account_info(
            info=self.key_data.model_dump(exclude_defaults=True)
        )
