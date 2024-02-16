import typing as t

import pytest
from typing import Union
from pydantic import ValidationError, Field, BaseModel
from devtools import debug

# from spice_rack import pydantic_bases

# todo: fix import
from spice_rack import _bases
dispatchable = _bases.dispatchable


class AbstractClass(dispatchable.DispatchedModelMixin["base", "root"]):
    root_field: str


class ChildClass1(AbstractClass["child1", "concrete"]):
    ...


class ChildClass2(AbstractClass["child2", "concrete"]):
    ...


class AbstractPassthroughChild(AbstractClass[("passthrough_child", "base")]):
    ...


class GrandchildClass1(AbstractPassthroughChild[("gc1", "concrete")]):
    ...


class GrandchildClass2(AbstractPassthroughChild[("gc2", "concrete")]):
    ...


class ClassDispatcher(dispatchable.DispatchedClassContainer[AbstractClass]):
    ...


@pytest.fixture(scope="function")  # keep function score bc we mutate it
def child_kwargs() -> dict:
    return {"root_field": ""}


def test_class_builds_correctly(child_kwargs):
    debug(ChildClass1.model_fields)
    class_type_field = ChildClass1.model_fields.get("class_type")
    assert class_type_field

    expected_class_type = "child1"
    inst = ChildClass1.model_validate(child_kwargs)
    assert inst
    assert inst.class_type == expected_class_type


def test_discrim_field_strict(child_kwargs):
    debug(ChildClass1.model_fields)
    debug(ChildClass2.model_fields)
    child_kwargs["class_type"] = ChildClass1.get_class_type()
    assert ChildClass1.model_validate(child_kwargs)
    debug(child_kwargs)
    with pytest.raises(ValidationError):
        bad_inst = ChildClass2(**child_kwargs)
        debug(bad_inst)


def test_child_dispatch_root_based(child_kwargs):
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_type"] = ChildClass1.get_class_type()

    dispatch_res = ClassDispatcher.model_validate(child_kwargs)
    assert isinstance(dispatch_res.root, ChildClass1)
    assert dispatch_res.root.class_type == ChildClass1.get_class_type()
    child_kwargs = dispatch_res.model_dump()

    child_kwargs["class_type"] = ChildClass2.get_class_type()
    dispatch_res = ClassDispatcher.validate(child_kwargs)
    assert isinstance(dispatch_res.root, ChildClass2)
    assert dispatch_res.root.class_type == ChildClass2.get_class_type()


def test_child_dispatch_type_adapter(child_kwargs):
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    dispatcher = AbstractClass.build_dispatcher_type_adapter()

    # dispatches based on class id
    child_kwargs["class_type"] = ChildClass1.get_class_type()

    dispatch_res = dispatcher.validate_python(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)
    assert dispatch_res.class_type == ChildClass1.get_class_type()
    child_kwargs = dispatch_res.model_dump()

    child_kwargs["class_type"] = ChildClass2.get_class_type()
    dispatch_res = dispatcher.validate_python(child_kwargs)
    assert isinstance(dispatch_res, ChildClass2)
    assert dispatch_res.class_type == ChildClass2.get_class_type()


def test_grandchild_dispatch(child_kwargs):
    child_kwargs["class_type"] = GrandchildClass1.get_class_type()
    dispatch_res = AbstractClass.build_dispatcher_type_adapter().validate_python(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_grandchild_dispatch_from_child(child_kwargs):
    child_kwargs["class_type"] = GrandchildClass1.get_class_type()
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
                ChildClass1.get_class_type(): '#/$defs/ChildClass1',
                ChildClass2.get_class_type(): '#/$defs/ChildClass2',
                GrandchildClass1.get_class_type(): '#/$defs/GrandchildClass1',
                GrandchildClass2.get_class_type(): '#/$defs/GrandchildClass2'
            },
            'propertyName': 'class_type',
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
                GrandchildClass1.get_class_type(): '#/$defs/GrandchildClass1',
                GrandchildClass2.get_class_type(): '#/$defs/GrandchildClass2'
            },
            'propertyName': 'class_type',
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
    import devtools
    devtools.debug(schema)
    assert schema == GrandchildClass1.model_json_schema()
