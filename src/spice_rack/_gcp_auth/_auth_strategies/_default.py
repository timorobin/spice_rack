from __future__ import annotations
import typing as t
import pydantic
from google.auth import credentials, default as gcp_default, exceptions as gcp_exceptions  # noqa

from spice_rack._gcp_auth._auth_strategies import _base


__all__ = (
    "DefaultAuthStrategy",
)


class DefaultAuthStrategy(_base.AbstractGcpAuthStrategy):
    """
    just ride with whatever defaults we have, works if we are in a vm and things like that
    see `docs <https://googleapis.dev/python/google-api-core/latest/auth.html#authentication>`_

    If nothing found we'll use anonymous.
    """
    on_no_default:  t.Literal["raise", "use_anon"] = pydantic.Field(
        description="What to do if GCP's default credential builder fails to find anything"
                    " in the environment. Choices are: 'raise', and 'use_anon'",
        default="use_anon"
    )

    def default_creds_found(self) -> bool:
        try:
            credentials_inst, _ = gcp_default()

        except gcp_exceptions.DefaultCredentialsError:
            return False

        except Exception as e:
            raise e

    def build_gcp_creds(
            self
    ) -> credentials.Credentials:
        """
        builds the GCP credentials object.

        Returns: The GCP Credentials instance

        Raises:
            DefaultCredentialsError if we fail to find the creds in the environment and the
                "on_no_default" is set to "raise"
        """
        # see:
        #   https://googleapis.dev/python/google-api-core/latest/auth.html#user-accounts-3-legged-oauth-2-0-with-a-refresh-token

        try:
            credentials_inst, _ = gcp_default()

        except gcp_exceptions.DefaultCredentialsError as e:
            if self.on_no_default == "raise":
                raise e
            elif self.on_no_default == "use_anon":
                credentials_inst = credentials.AnonymousCredentials()
            else:
                raise ValueError(
                    f"unexpected value for 'on_no_default' param: '{self.on_no_default}'"
                )

        return credentials_inst
