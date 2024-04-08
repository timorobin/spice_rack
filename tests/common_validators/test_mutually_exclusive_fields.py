import pytest
import typing as t
import pydantic

from spice_rack import bases, common_validators


def test_val_inst():
    val_inst = common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsValidator(
        field_names=["a", "b", "c"],
    )

    class X(bases.PydanticBase):
        a: t.Optional[str] = None
        b: t.Optional[str] = None
        c: t.Optional[str] = None

    x_good = X(a="a")
    x_multiple = X(a="a", b="b")
    x_none = X()

    assert val_inst.validate_inst(x_good)

    with pytest.raises(common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsException):
        val_inst.validate_inst(x_multiple)

    with pytest.raises(common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsException):
        val_inst.validate_inst(x_none)


def test_as_on_model():
    val_inst = common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsValidator(
        field_names=["a", "b", "c"],
    )

    class X(bases.PydanticBase):
        a: t.Optional[str] = None
        b: t.Optional[str] = None
        c: t.Optional[str] = None

        def _post_init_validation(self) -> None:
            val_inst.validate_inst(self)
            return

    assert X(c="a")

    with pytest.raises(pydantic.ValidationError):
        X(a="a", b="b")

    with pytest.raises(pydantic.ValidationError):
        X()


def test_as_ann():
    class X(bases.PydanticBase):
        a: t.Optional[str] = None
        b: t.Optional[str] = None
        c: t.Optional[str] = None

    class D(pydantic.BaseModel):
        x: t.Annotated[
            X,
            common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsValidator(
                field_names=["a", "b", "c"],
            )
        ]

    x_good = X(b="a")
    x_multiple = X(a="a", b="b")
    x_none = X()

    assert D(x=x_good)

    with pytest.raises(pydantic.ValidationError):
        D(x=x_multiple)

    with pytest.raises(pydantic.ValidationError):
        D(x=x_none)


def test_val_model_cls_field_check():
    class X(bases.PydanticBase):
        a: t.Optional[str] = None
        b: t.Optional[str] = None

    with pytest.raises(ValueError):
        common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsValidator(
            field_names=["a", "b", "c"],
            model_cls=X,
            check_field_names=True
        )


def test_all_none_allowed():

    class X(bases.PydanticBase):
        a: t.Optional[str] = None
        b: t.Optional[str] = None
        c: t.Optional[str] = None

    class D(pydantic.BaseModel):
        x: t.Annotated[
            X,
            common_validators.mutually_exclusive_fields.MutuallyExclusiveFieldsValidator(
                field_names=["a", "b", "c"],
                at_least_one=False
            ),
        ]

    x_good = X(b="a")
    x_multiple = X(a="a", b="b")
    x_none = X()

    assert D(x=x_good)
    assert D(x=x_none)

    with pytest.raises(pydantic.ValidationError):
        D(x=x_multiple)
