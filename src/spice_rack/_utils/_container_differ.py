from __future__ import annotations
from typing import Sequence, TypeVar, Hashable


__all__ = (
    "get_difference_between_string_seqs",
    "get_difference_between_sets"
)


def get_difference_between_string_seqs(
        a: Sequence[str], b: Sequence[str]
) -> tuple[list[str], list[str]]:
    """
    compares 2 sequences of strings and returns the strings
    in A not in B and the strings in B not in A
    """
    a_set = set([str(aa) for aa in a])
    b_set = set([str(bb) for bb in b])

    in_a_not_b = [aa for aa in a_set if aa not in b]
    in_b_not_a = [bb for bb in b_set if bb not in a]
    return sorted(in_a_not_b), sorted(in_b_not_a)


SetItemTV = TypeVar("SetItemTV", bound=Hashable)


def get_difference_between_sets(
        a: set[SetItemTV],
        b: set[SetItemTV]
) -> tuple[set[SetItemTV], set[SetItemTV]]:
    total_items = a.union(b)

    items_in_a_not_b = set()
    items_in_b_not_a = set()

    for item in total_items:
        if item not in a:
            items_in_b_not_a.add(item)
        elif item not in b:
            items_in_a_not_b.add(item)
    return items_in_a_not_b, items_in_b_not_a
