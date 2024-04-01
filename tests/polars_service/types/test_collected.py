import polars as pl

from spice_rack import polars_service, bases


class _FakeModel(bases.RootModel[polars_service.types.PolarsDfT]):

    def __eq__(self, other: pl.DataFrame) -> bool:
        return self.root.to_dict(as_series=False) == other.to_dict(as_series=False)


def test_parse_collected_df(sample_df):
    obj = _FakeModel.model_validate(sample_df)
    assert isinstance(obj.root, pl.DataFrame)
    assert obj == sample_df


def test_parse_lazy_df(sample_df):
    obj = _FakeModel.model_validate(sample_df.lazy())
    assert isinstance(obj.root, pl.DataFrame)
    assert obj == sample_df


def test_parse_row_dicts(sample_df):
    obj = _FakeModel.model_validate(sample_df.to_dicts())
    assert isinstance(obj.root, pl.DataFrame)
    assert obj == sample_df


def test_parse_columnar_dict(sample_df):
    obj = _FakeModel.model_validate(sample_df.to_dict(as_series=False))
    assert isinstance(obj.root, pl.DataFrame)
    assert obj == sample_df


def test_model_dump_python(sample_df):
    obj = _FakeModel.model_validate(sample_df)
    dumped = obj.model_dump(mode="python")
    assert isinstance(dumped, pl.DataFrame)
    assert dumped.to_dict(as_series=False) == sample_df.to_dict(as_series=False)


def test_model_dump_json(sample_df, sample_df_json_dumped):
    obj = _FakeModel.model_validate(sample_df)
    dumped = obj.model_dump(mode="json")
    assert isinstance(dumped, list)
    assert dumped == sample_df_json_dumped
