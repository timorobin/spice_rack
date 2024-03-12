import pytest

from ._config import TestConfig


@pytest.fixture(scope="session")
def session_config() -> TestConfig:
    return TestConfig.load()
