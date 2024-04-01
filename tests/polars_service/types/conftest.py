import pytest
import datetime as dt
import polars as pl

from spice_rack import polars_service


@pytest.fixture(scope="package")
def sample_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "a": [0, 1, 2, 3],
            "b": ["a", "b", 'c', "d"],
            "c": [[1, 0], [0, 2], [1, 3], [24, 1]],
            "d": [dt.datetime.now()] * 4
        }
    )


@pytest.fixture(scope="package")
def sample_df_json_dumped(sample_df) -> polars_service.types.RowDictsJsonDumpedT:
    return polars_service.services.get_json_safe_row_dicts(sample_df)
