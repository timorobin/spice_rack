import pytest
import typing as t

from spice_rack import heap


class SomeItem:
    def __init__(self, val: int):
        self.val = val


@pytest.fixture(scope="module")
def sample_items() -> t.List[SomeItem]:
    return [
        SomeItem(10),
        SomeItem(5),
        SomeItem(11),
        SomeItem(1)
    ]


def test_min_heap(sample_items):
    heap_inst = heap.MinHeap[SomeItem](
        key_fn=lambda _: _.val
    )

    for item in sample_items:
        heap_inst.push(item)

    assert len(heap_inst) == len(sample_items)
    popped_heap = []
    while heap_inst:
        popped_heap.append(heap_inst.pop())

    assert sorted([i.val for i in sample_items]) == [i.val for i in popped_heap]


def test_max_heap(sample_items):
    heap_inst = heap.MinHeap[SomeItem](
        key_fn=lambda _: -_.val
    )

    for item in sample_items:
        heap_inst.push(item)

    assert len(heap_inst) == len(sample_items)
    popped_heap = []
    while heap_inst:
        popped_heap.append(heap_inst.pop())

    assert sorted([i.val for i in sample_items], reverse=True) == [i.val for i in popped_heap]
