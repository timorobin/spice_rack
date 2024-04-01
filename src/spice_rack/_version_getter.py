from importlib.metadata import version


__all__ = (
    "get_version",
)


def get_version(package_name: str) -> str:
    return version(package_name)
