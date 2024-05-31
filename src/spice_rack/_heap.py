"""simple heap class bc using the functional heapq lib was annoying. Not sure when I'd actually ever use this
thing other than leetcode, where I can't use this package anyway.
"""

from __future__ import annotations
import typing as t
import heapq
import functools
import dataclasses as dc


__all__ = (
    "MinHeap",
)


ItemTV = t.TypeVar("ItemTV", )


@functools.total_ordering
@dc.dataclass
class _MinHeapEntry(t.Generic[ItemTV]):
    key: t.Any
    item: ItemTV

    def __eq__(self, other: _MinHeapEntry) -> bool:
        if not isinstance(other, _MinHeapEntry):
            raise ValueError(
                f"can only compare MinHeapEntry to MinHeapEntry, "
                f"encountered {type(other)}"
            )
        return self.key == other.key

    def __lt__(self, other: _MinHeapEntry) -> bool:
        if not isinstance(other, _MinHeapEntry):
            raise ValueError(
                f"can only compare MinHeapEntry to MinHeapEntry, "
                f"encountered {type(other)}"
            )
        return self.key < other.key


class MinHeap(t.Generic[ItemTV]):
    """
    implement a min heap as a class. Specify a custom key_fn if you want to
    control how the heap is sorted. When we add an item, we pass it through the key
    function to get a key value that we use to sort.
    """
    _entries: t.List[_MinHeapEntry[ItemTV]]
    _key_fn: t.Callable[[ItemTV, ], t.Any]

    def __init__(
            self,
            key_fn: t.Callable[[ItemTV, ], t.Any]
    ):
        self._entries = []
        self._key_fn = key_fn

    def push(self, __item: ItemTV) -> None:
        key = self._key_fn(__item)
        entry = _MinHeapEntry(
            key=key,
            item=__item
        )
        heapq.heappush(self._entries, entry)

    def pop(self) -> ItemTV:
        try:
            entry = heapq.heappop(self._entries)
        except IndexError as e:
            raise e

        return entry.item

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_list(self) -> t.List[ItemTV]:
        return [entry.item for entry in self._entries]
