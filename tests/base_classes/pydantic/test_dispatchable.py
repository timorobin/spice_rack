import typing as t

import pytest
from typing import Union
from pydantic import ValidationError, Field, BaseModel
from devtools import debug

# from spice_rack import pydantic_bases

# todo: fix import
from spice_rack import base_classes
from spice_rack._base_classes._pydantic._dispatchable import _ClassIdEnumTV, DispatchableModelMixin

dispatchable = base_classes.pydantic.dispatchable


class ClassTypes(dispatchable.ConcreteClassIdEnumBase):
    CHILD1 = "child1"
    CHILD2 = "child2"
    GRANDCHILD1 = "grandchild1"
    GRANDCHILD2 = "grandchild2"


class AbstractClass(dispatchable.DispatchableModelMixin[ClassTypes], is_new_root=True):
    root_field: str
        
    @classmethod
    def get_cls_id(cls) -> t.Optional[ClassTypes]:
        return None
    
    
class ChildClass1(AbstractClass, is_concrete=True):
    @classmethod
    def get_cls_id(cls) -> t.Optional[ClassTypes]:
        return ClassTypes.CHILD1


class ChildClass2(AbstractClass, is_concrete=True):
    @classmethod
    def get_cls_id(cls) -> t.Optional[ClassTypes]:
        return ClassTypes.CHILD2


@pytest.fixture(scope="function")  # keep function score bc we mutate it
def child_kwargs() -> dict:
    return {"root_field": ""}


def test_class_builds_correctly(child_kwargs):
    debug(ChildClass1.__fields__)
    class_id_field = ChildClass1.__fields__.get("class_id")
    assert class_id_field

    expected_class_id = ClassTypes.CHILD1.value
    assert class_id_field.default == expected_class_id
    inst = ChildClass1.validate(child_kwargs)
    assert inst
    assert inst.class_id == expected_class_id


def test_discrim_field_strict(child_kwargs):
    debug(ChildClass1.__fields__)
    debug(ChildClass2.__fields__)
    child_kwargs["class_id"] = ChildClass1.get_cls_id_str()
    assert ChildClass1.parse_obj(child_kwargs)
    debug(child_kwargs)
    with pytest.raises(ValidationError):
        bad_inst = ChildClass2(**child_kwargs)
        debug(bad_inst)


def test_child_dispatch(child_kwargs):
    # no class id
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_id"] = ChildClass1.get_cls_id_str()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)
    assert dispatch_res.class_id == ChildClass1.get_cls_id_str()
    child_kwargs = dispatch_res.dict()

    child_kwargs["class_id"] = ChildClass2.get_cls_id_str()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass2)
    assert dispatch_res.class_id == ChildClass2.get_cls_id_str()


def test_child_dispatch_json(child_kwargs):

    # no class id
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_id"] = ChildClass1.get_cls_id_str()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)

    child_kwargs_json = dispatch_res.json()
    json_dispatch_res = AbstractClass.parse_raw(child_kwargs_json)
    assert json_dispatch_res.class_id == ChildClass1.get_cls_id_str()
    assert isinstance(json_dispatch_res, ChildClass1)


class AbstractPassthroughChild(AbstractClass):
    ...


class GrandchildClass1(AbstractPassthroughChild, is_concrete=True):

    @classmethod
    def get_cls_id(cls) -> t.Optional[ClassTypes]:
        return ClassTypes.GRANDCHILD1


class GrandchildClass2(AbstractPassthroughChild, is_concrete=True):
    @classmethod
    def get_cls_id(cls) -> t.Optional[ClassTypes]:
        return ClassTypes.GRANDCHILD2


def test_family_built_correctly():
    assert ChildClass1._root_cls_registry._root_cls == AbstractClass

    keys_found = [str(cls.get_cls_id_str()) for cls in AbstractClass.iter_concrete_subclasses()]
    keys_expected = [
        ChildClass1.get_cls_id_str(), ChildClass2.get_cls_id_str(),
        GrandchildClass1.get_cls_id_str(), GrandchildClass2.get_cls_id_str()
    ]

    assert keys_found == keys_expected


def test_grandchild_dispatch(child_kwargs):
    child_kwargs["class_id"] = GrandchildClass1.get_cls_id_str()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_grandchild_dispatch_from_child(child_kwargs):
    child_kwargs["class_id"] = GrandchildClass1.get_cls_id_str()
    dispatch_res = AbstractPassthroughChild.validate(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_schema_gen():

    class PayloadTypes(dispatchable.ConcreteClassIdEnumBase):
        A = "a"
        B = "b"

    class AbstractPayload(
        dispatchable.DispatchableModelMixin[PayloadTypes],
        is_new_root=True
    ):
        common_f: str

        @classmethod
        def get_cls_id(cls) -> t.Optional[PayloadTypes]:
            return None

    class ConcretePayloadA(AbstractPayload, is_concrete=True):
        a_f: str

        @classmethod
        def get_cls_id(cls) -> t.Optional[PayloadTypes]:
            return PayloadTypes.A

    class ConcretePayloadB(AbstractPayload, is_concrete=True):
        b_f: str

        @classmethod
        def get_cls_id(cls) -> t.Optional[PayloadTypes]:
            return PayloadTypes.B

    class PayloadContainer(BaseModel):
        f1: AbstractPayload
        f2: Union[ConcretePayloadA, ConcretePayloadB]
        f3: AbstractPayload.build_union_type()
        f4: AbstractPayload.build_union_type() = Field(discriminator="class_id")

    schema = PayloadContainer.schema()
    f1_schema = schema["properties"]["f1"]
    f2_schema = schema["properties"]["f2"]
    f3_schema = schema["properties"]["f3"]
    f4_schema = schema["properties"]["f4"]

    # f1 should just be the root class
    assert f1_schema == {'$ref': '#/definitions/AbstractPayload'}

    # f2 and f3 should be equivalent, the schema from Union of the concretes
    union_schema = {
        'anyOf': [
            {
                '$ref': '#/definitions/ConcretePayloadA',
            },
            {
                '$ref': '#/definitions/ConcretePayloadB',
            },
        ],
    }
    assert f2_schema == {'title': 'F2', **union_schema}
    assert f3_schema == {'title': 'F3', **union_schema}

    # f4 is a special discriminated union type
    assert f4_schema == {
        'title': 'F4',
        'discriminator': {
            'propertyName': 'class_id',
            'mapping': {
                'a': '#/definitions/ConcretePayloadA',
                'b': '#/definitions/ConcretePayloadB',
            },
        },
        'oneOf': [
            {
                '$ref': '#/definitions/ConcretePayloadA',
            },
            {
                '$ref': '#/definitions/ConcretePayloadB',
            },
        ],
    }

    from devtools import debug
    debug(schema)

    # this should still work for all fields
    payload_raw = {"class_id": "b", "common_f": "x", "b_f": "y"}
    payload_obj = AbstractPayload.validate(payload_raw)

    # Important notes below:
    #  The type checker complains about f2 but doesn't complain about f3 or f4.
    #  This is because even f2 is Union[ConcretePayloadA, ConcretePayloadB]
    #   and the obj we passed is AbstractPayload. Even though f3 and f4's annotation
    #   are actually the exact same object as f2's, Union[ConcretePayloadA, ConcretePayloadB],
    #   the type checker thinks it is the same annotation as f1, AbstractPayload.
    #
    # Regardless of type checker behavior, all 4 fields should be fine at runtime

    obj = PayloadContainer(
        f1=payload_obj,
        f2=payload_obj,
        f3=payload_obj,
        f4=payload_obj
    )
    assert obj
