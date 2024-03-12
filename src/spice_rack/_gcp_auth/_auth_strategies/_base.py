from __future__ import annotations
from abc import abstractmethod

from google.auth import credentials  # noqa

from spice_rack import _bases


__all__ = (
    "AbstractGcpAuthStrategy",
)


class AbstractGcpAuthStrategy(
    _bases.dispatchable.DispatchableValueModelBase,
    class_type="root",
    class_id="gcp_auth_strat_base"
):
    """
    base class for all the ways we can authenticate to gcs.
    see `docs <https://googleapis.dev/python/google-api-core/latest/auth.html#authentication>`_
    """

    @abstractmethod
    def build_gcp_creds(self) -> credentials.Credentials:
        """
        builds the GCP credentials object, based on this strategy.

        Returns: The GCP Credentials instance
        """
        ...
