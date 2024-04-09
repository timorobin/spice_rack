from typing import Any

import pydantic
import pytest
from pydantic import ValidationError, BaseModel
from devtools import debug


from spice_rack import bases
dispatchable = bases.dispatchable


class AbstractClass(dispatchable.DispatchedModelMixin):
    root_field: str


class ChildClass1(AbstractClass, class_id="child1"):
    ...


class ChildClass2(AbstractClass, class_id="child2"):
    ...


class AbstractPassthroughChild(AbstractClass, class_type="root", class_id="root_child"):
    ...


class GrandchildClass1(AbstractPassthroughChild, class_id="gc1"):
    ...


class GrandchildClass2(AbstractPassthroughChild, class_id="gc2"):
    ...


class ClassDispatcher(dispatchable.DispatchedClassContainer[AbstractClass]):
    ...


def test_class_attrs():
    assert ChildClass1.get_class_id_path() == ("abstract_class", "child1")
    assert GrandchildClass1.get_class_id_path() == (
        "abstract_class", "root_child", "gc1"
    )


@pytest.fixture(scope="function")  # keep function score bc we mutate it
def child_kwargs() -> dict:
    return {"root_field": ""}


def test_class_builds_correctly(child_kwargs):
    debug(ChildClass1.model_fields)
    class_type_field = ChildClass1.model_fields.get("class_id")
    assert class_type_field

    expected_class_type = "child1"
    inst = ChildClass1.model_validate(child_kwargs)
    assert inst
    assert inst.class_id == expected_class_type


def test_discrim_field_strict(child_kwargs):
    debug(ChildClass1.model_fields)
    debug(ChildClass2.model_fields)
    child_kwargs["class_id"] = "child1"
    assert ChildClass1.model_validate(child_kwargs)
    debug(child_kwargs)
    with pytest.raises(ValidationError):
        bad_inst = ChildClass2(**child_kwargs)
        debug(bad_inst)


def test_child_dispatch_root_based(child_kwargs):
    with pytest.raises(ValueError):
        AbstractClass.model_validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_id"] = "child1"

    dispatch_res = ClassDispatcher.model_validate(child_kwargs)
    assert isinstance(dispatch_res.root, ChildClass1)
    assert dispatch_res.root.class_id == "child1"
    child_kwargs = dispatch_res.model_dump()

    child_kwargs["class_id"] = "child2"
    dispatch_res = ClassDispatcher.model_validate(child_kwargs)
    assert isinstance(dispatch_res.root, ChildClass2)
    assert dispatch_res.root.class_id == "child2"


def test_child_dispatch_type_adapter(child_kwargs):
    with pytest.raises(ValueError):
        AbstractClass.model_validate(child_kwargs)

    dispatcher = AbstractClass.build_dispatcher_type_adapter()

    # dispatches based on class id
    child_kwargs["class_id"] = "child1"

    dispatch_res = dispatcher.validate_python(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)
    assert dispatch_res.class_id == "child1"
    child_kwargs = dispatch_res.model_dump()

    child_kwargs["class_id"] = "child2"
    dispatch_res = dispatcher.validate_python(child_kwargs)
    assert isinstance(dispatch_res, ChildClass2)
    assert dispatch_res.class_id == "child2"


def test_grandchild_dispatch(child_kwargs):
    child_kwargs["class_id"] = "gc1"
    dispatch_res = AbstractClass.build_dispatcher_type_adapter().validate_python(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_grandchild_dispatch_from_child(child_kwargs):
    child_kwargs["class_id"] = "gc1"
    dispatch_res = AbstractPassthroughChild.build_dispatcher_type_adapter().validate_python(
        child_kwargs
    )
    assert isinstance(dispatch_res, GrandchildClass1)


def test_schema_gen():
    schema = AbstractClass.build_dispatcher_type_adapter().json_schema()
    import devtools
    devtools.debug(schema)
    assert schema == {
        "$defs": {
            "ChildClass1": ChildClass1.model_json_schema(),
            "ChildClass2": ChildClass2.model_json_schema(),
            "GrandchildClass1": GrandchildClass1.model_json_schema(),
            "GrandchildClass2": GrandchildClass2.model_json_schema(),
        },
        "discriminator": {
            "mapping": {
                "child1": '#/$defs/ChildClass1',
                "child2": '#/$defs/ChildClass2',
                "gc1": '#/$defs/GrandchildClass1',
                "gc2": '#/$defs/GrandchildClass2'
            },
            'propertyName': 'class_id',
        },
        'oneOf': [
            {
                '$ref': '#/$defs/ChildClass1',
            },
            {
                '$ref': '#/$defs/ChildClass2',
            },
            {
                '$ref': '#/$defs/GrandchildClass1',
            },
            {
                '$ref': '#/$defs/GrandchildClass2',
            },
        ],
    }


def test_schema_gen_intermediate():
    schema = AbstractPassthroughChild.build_dispatcher_type_adapter().json_schema()
    import devtools
    devtools.debug(schema)
    assert schema == {
        "$defs": {
            "GrandchildClass1": GrandchildClass1.model_json_schema(),
            "GrandchildClass2": GrandchildClass2.model_json_schema(),
        },
        "discriminator": {
            "mapping": {
                "gc1": '#/$defs/GrandchildClass1',
                "gc2": '#/$defs/GrandchildClass2'
            },
            'propertyName': 'class_id',
        },
        'oneOf': [
            {
                '$ref': '#/$defs/GrandchildClass1',
            },
            {
                '$ref': '#/$defs/GrandchildClass2',
            },
        ],
    }


def test_schema_gen_concrete():
    schema = GrandchildClass1.build_dispatcher_type_adapter().json_schema()
    assert schema == GrandchildClass1.model_json_schema()

    from devtools import pprint
    print("original")
    pprint(
        # GrandchildClass1.model_json_schema()
        GrandchildClass1.__pydantic_core_schema__["schema"]["schema"]["schema"]["fields"]
    )

    print("changed")
    GrandchildClass1.model_fields["class_id"] = pydantic.fields.FieldInfo.from_annotation(int)
    GrandchildClass1.model_rebuild(force=True)

    pprint(
        # GrandchildClass1.model_json_schema()
        GrandchildClass1.__pydantic_core_schema__["schema"]["schema"]["schema"]["fields"]
    )

    # raise ValueError()


def test_as_field():
    base_t = AbstractClass.build_dispatched_ann()

    class X(BaseModel):
        f: base_t

    x = X.model_validate(
        {"f": {"root_field": "", "class_id": "gc1"}}
    )

    assert isinstance(x.f, GrandchildClass1)
