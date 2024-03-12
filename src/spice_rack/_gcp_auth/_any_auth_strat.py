from __future__ import annotations

try:
    from google.auth import credentials  # noqa
except ImportError:
    raise ValueError(
        "cannot use the gcp auth module bc google.auth isn't installed"
    )

from spice_rack import _bases
from spice_rack._gcp_auth import _auth_strategies


__all__ = (
    "AnyGcpAuthStrat",
)


class AnyGcpAuthStrat(
    _bases.dispatchable.DispatchedClassContainer[_auth_strategies.AbstractGcpAuthStrategy]
):
    """container class that holds the different types of gcp auth strategies"""
    def build_gcp_creds(self) -> credentials.Credentials:
        """
        builds the GCP credentials object, based on this strategy.

        Returns: The GCP Credentials instance
        """
        return self.root.build_gcp_creds()

    @classmethod
    def init_default(cls) -> AnyGcpAuthStrat:
        strat = _auth_strategies.DefaultAuthStrategy()
        return AnyGcpAuthStrat.model_validate(strat)
