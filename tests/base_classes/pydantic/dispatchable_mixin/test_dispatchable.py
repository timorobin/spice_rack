import pytest
from typing import Union
from pydantic import ValidationError, Field, BaseModel
from devtools import debug

from spice_rack import pydantic_bases


class AbstractClass(pydantic_bases.dispatchable.DispatchableModelMixin):
    root_field: str


class ChildClass1(AbstractClass):
    ...


class ChildClass2(AbstractClass):
    ...


@pytest.fixture(scope="function")  # keep function score bc we mutate it
def child_kwargs() -> dict:
    return {"root_field": ""}


def test_class_builds_correctly(child_kwargs):
    debug(ChildClass1.__fields__)
    class_id_field = ChildClass1.__fields__.get("class_id")
    assert class_id_field

    expected_class_id = "AbstractClass.ChildClass1"
    assert class_id_field.default == expected_class_id
    inst = ChildClass1.validate(child_kwargs)
    assert inst.class_id == expected_class_id


def test_discrim_field_strict(child_kwargs):
    child_kwargs["class_id"] = ChildClass1.get_class_id()
    assert ChildClass1.parse_obj(child_kwargs)

    with pytest.raises(ValidationError):
        ChildClass2(**child_kwargs)


def test_child_dispatch(child_kwargs):
    # no class id
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_id"] = ChildClass1.get_class_id()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)
    assert dispatch_res.class_id == ChildClass1.get_class_id()
    child_kwargs = dispatch_res.dict()

    child_kwargs["class_id"] = ChildClass2.get_class_id()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass2)
    assert dispatch_res.class_id == ChildClass2.get_class_id()


def test_child_dispatch_json(child_kwargs):

    # no class id
    with pytest.raises(ValueError):
        AbstractClass.validate(child_kwargs)

    # dispatches based on class id
    child_kwargs["class_id"] = ChildClass1.get_class_id()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, ChildClass1)

    child_kwargs_json = dispatch_res.json()
    json_dispatch_res = AbstractClass.parse_raw(child_kwargs_json)
    assert json_dispatch_res.class_id == ChildClass1.get_class_id()
    assert isinstance(json_dispatch_res, ChildClass1)


class AbstractPassthroughChild(AbstractClass):
    ...


class GrandchildClass1(AbstractPassthroughChild):
    ...


class GrandchildClass2(AbstractPassthroughChild):
    ...


def test_grandchild_dispatch(child_kwargs):
    child_kwargs["class_id"] = GrandchildClass1.get_class_id()
    dispatch_res = AbstractClass.validate(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_grandchild_dispatch_from_child(child_kwargs):
    child_kwargs["class_id"] = GrandchildClass1.get_class_id()
    dispatch_res = AbstractPassthroughChild.validate(child_kwargs)
    assert isinstance(dispatch_res, GrandchildClass1)


def test_family_built_correctly():
    assert ChildClass1.get_family_tree().root_cls == AbstractClass

    family_tree_ = AbstractClass.get_family_tree()

    keys_found = [str(cls.get_class_id()) for cls in family_tree_.iter_members()]
    keys_expected = [
        ChildClass1.get_class_id(), ChildClass2.get_class_id(),
        AbstractPassthroughChild.get_class_id(),
        GrandchildClass1.get_class_id(), GrandchildClass2.get_class_id()
    ]

    assert keys_found == keys_expected


def test_schema_gen():
    class AbstractPayload(pydantic_bases.dispatchable.DispatchableModelMixin):
        common_f: str

    class ConcretePayloadA(AbstractPayload):
        a_f: str

    class ConcretePayloadB(AbstractPayload):
        b_f: str

    class PayloadContainer(BaseModel):
        f1: AbstractPayload
        f2: Union[ConcretePayloadA, ConcretePayloadB]
        f3: AbstractPayload.build_concrete_union_type_ann()
        f4: AbstractPayload.build_concrete_union_type_ann() = Field(discriminator="class_id")

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
                'AbstractPayload.ConcretePayloadA': '#/definitions/ConcretePayloadA',
                'AbstractPayload.ConcretePayloadB': '#/definitions/ConcretePayloadB',
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
    payload_raw = {"class_id": "AbstractPayload.ConcretePayloadB", "common_f": "x", "b_f": "y"}
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
