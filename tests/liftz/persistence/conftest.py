import pytest
from pathlib import Path

from liftz import persistence


@pytest.fixture(scope="session")
def db_file_path() -> Path:
    path_obj = Path(__file__).parent.joinpath("persistence_tests.db")
    yield path_obj
    path_obj.unlink(missing_ok=True)


@pytest.fixture(scope="session", autouse=True)
async def init_db(db_file_path) -> None:
    db_path = f"sqlite:///{str(db_file_path.absolute())}"
    await persistence.db_init(db_uri=db_path)
    yield
    await persistence.db_close()

