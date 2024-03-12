from __future__ import annotations
from google.auth import credentials  # noqa

from spice_rack._gcp_auth._auth_strategies import _base


__all__ = (
    "AnonAuthStrategy",
)


class AnonAuthStrategy(_base.AbstractGcpAuthStrategy):
    """
    Authenticate to the client as anonymous.
    """

    def build_gcp_creds(self) -> credentials.Credentials:
        return credentials.AnonymousCredentials()
