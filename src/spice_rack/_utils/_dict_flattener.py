from __future__ import annotations
import typing as t

from flatten_dict import flatten


__all__ = (
    "flatten_dict",
)


# restrict support for non-string based key reducers to allow us to enforce type annotation on the key


_REDUCER_FUNC_T = t.Callable[[t.Optional[t.Hashable], t.Hashable], str]
"""
type ann for a key reducer for the flattener. I inferred this from the source code here
https://github.com/ianlini/flatten-dict/blob/master/src/flatten_dict/reducers.py
"""


class _CustomSepReducerFunc:
    def __init__(self, sep: str):
        self.sep = sep

    def __call__(self, k1: t.Optional[t.Hashable], k2: t.Optional[t.Hashable]) -> str:
        pieces: t.List[str] = []
        if k1:
            pieces.append(str(k1))
            pieces.append(self.sep)
        pieces.append(str(k2))
        return "".join(pieces)


def flatten_dict(
        __dict: t.Dict[t.Any, t.Any],
        *,
        key_join_strat: t.Union[str, _REDUCER_FUNC_T] = "__",
        enumerate_types: t.Iterable[type] = (list, ),
        max_flatten_depth: t.Optional[int] = None,
        **kwargs
) -> t.Dict[str, t.Any]:
    """
    flatten the dict using https://github.com/ianlini/flatten-dict?tab=readme-ov-file#flatten

    Args:
        __dict: the dict to flatten
        key_join_strat: the strategy used to join keys when flattening, if a string is specified we treat is as
            shorthand for a func that joins keys using the str as the separator
        enumerate_types: an iterable of we want to enumerate, see doctest for example
        max_flatten_depth: specify this to restrict the depth we will flatten to. default is None, i.e. no restriction
        **kwargs: any other kwargs to pass through to https://github.com/ianlini/flatten-dict?tab=readme-ov-file#flatten

    Returns:
        a flattened dict

    >>> flatten_dict({"a": 1, "b": {"b": 1}})
    {'a': 1, 'b__b': 1}

    >>> flatten_dict({1: "a", 2: {2: "b"}})
    {'1': 'a', '2__2': 'b'}

    >>> flatten_dict({"a": ["x", "y", "z"]})
    {'a__0': 'x', 'a__1': 'y', 'a__2': 'z'}

    >>> flatten_dict({"a": ["x", "y", "z"]}, enumerate_types=())
    {'a': ['x', 'y', 'z']}
    """
    reducer_func: _REDUCER_FUNC_T
    if callable(key_join_strat):
        reducer_func = key_join_strat
    else:
        reducer_func = _CustomSepReducerFunc(sep=key_join_strat)
    return flatten(
        __dict,
        reducer=reducer_func,
        enumerate_types=enumerate_types,
        max_flatten_depth=max_flatten_depth,
        **kwargs
    )
