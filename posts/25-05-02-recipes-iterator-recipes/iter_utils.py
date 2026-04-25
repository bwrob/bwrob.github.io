"""Utilities for working with iterables."""

from __future__ import annotations

import itertools
import operator
from collections.abc import Callable, Generator, Iterable, Iterator, Mapping
from itertools import islice
from sys import maxsize
from typing import Protocol, Self, cast

type NestedDict[T] = Mapping[str, NestedDict[T] | T]
type NestedIterable[T] = Iterable[NestedIterable[T] | T]


def batched[T](
    iterable: Iterable[T],
    n: int,
    *,
    strict: bool = False,
) -> Iterable[tuple[T, ...]]:
    """Split an iterable into batches of size n."""
    if not 1 <= n <= maxsize:
        msg = "Batch size n must be at least one and at most sys.maxsize."
        raise ValueError(msg)

    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            msg = "Incomplete batch for strict batching."
            raise ValueError(msg)
        yield batch


def unbox[T](iterable: Iterable[T]) -> T:
    """Unbox an iterable if it contains a single element."""
    iterator = iter(iterable)
    first_value = next(iterator)
    try:
        _ = next(iterator)
        msg = "Iterable contains more than one element."
        raise ValueError(msg)
    except StopIteration:
        return first_value


def unzip[T](iterable: Iterable[tuple[T, ...]]) -> tuple[Iterable[T], ...]:
    """Unzip an iterable of tuples."""
    zipped = zip(*iterable, strict=True)
    return tuple(zipped)


def flatten_iterable[T](iterable: NestedIterable[T]) -> list[T]:
    """Flatten an iterable of iterables."""

    def _helper(lst: NestedIterable[T]) -> Generator[T]:
        for item in lst:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                yield from _helper(cast(NestedIterable[T], item))
            else:
                yield cast(T, item)

    return list(_helper(iterable))


def flatten_string_key_dict[T](dictionary: NestedDict[T]) -> dict[str, T]:
    """Flatten a nested string-keyed dictionary."""

    def _generate_items(
        d: NestedDict[T] | T, prefix: str = ""
    ) -> Generator[tuple[str, T]]:
        if isinstance(d, dict):
            for key, value in d.items():
                yield from _generate_items(value, prefix + key + ".")
        else:
            yield prefix[:-1], cast(T, d)

    return dict(_generate_items(dictionary))


class _SupportsLessThan(Protocol):
    def __lt__(self, other: Self) -> bool: ...


def group_by_non_consecutive[T, SLT: _SupportsLessThan](
    iterable: Iterable[T],
    *,
    key: Callable[[T], SLT] | None = None,
    reverse: bool = False,
) -> Iterator[tuple[SLT, Iterator[T]]]:
    """Sort and group an iterable by a key function.

    Unlike itertools.groupby, this function does not require the iterable
    to be pre-sorted. It first sorts the entire iterable and then applies
    the grouping.
    """
    if key is None:

        def default_key(x: T) -> SLT:
            return cast(SLT, x)

        key = default_key
    sorted_iterable = sorted(iterable, key=key, reverse=reverse)
    return itertools.groupby(sorted_iterable, key=key)


if __name__ == "__main__":
    # Example for batched
    print("--- batched ---")
    print(f"batched(range(10), 3): {list(batched(range(10), 3))}")
    print()

    # Example for unbox
    print("--- unbox ---")
    print(f"unbox([42]): {unbox([42])}")
    try:
        _ = unbox([1, 2])
    except ValueError as e:
        print(f"unbox([1, 2]): {e}")
    print()

    # Example for unzip
    print("--- unzip ---")
    zipped_data = [(1, "a"), (2, "b"), (3, "c")]
    unzipped_data = unzip(zipped_data)
    print(f"unzip({zipped_data}): {[list(it) for it in unzipped_data]}")
    print()

    # Example for flatten_iterable
    print("--- flatten_iterable ---")
    nested_list = [1, [2, "a", [3]], "b"]
    print(f"flatten_iterable({nested_list}): {flatten_iterable(nested_list)}")
    print()

    # Example for flatten_string_key_dict
    print("--- flatten_string_key_dict ---")
    nested_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": 4}
    print(
        f"flatten_string_key_dict({nested_dict}): "
        + f"{flatten_string_key_dict(nested_dict)}"
    )
    print()

    # Example for group_by_non_consecutive
    print("--- group_by_non_consecutive ---")
    # With key function
    data = ["apple", "banana", "ant", "bear", "apricot"]
    print(f"group_by_non_consecutive({data}, key=lambda x: x[0])")
    for key, group in group_by_non_consecutive(data, key=operator.itemgetter(0)):
        print(f"  {key}: {list(group)}")
    print()

    # Without key function
    data_nums = [1, 2, 1, 3, 2, 1]
    print(f"group_by_non_consecutive({data_nums})")
    for key, group in group_by_non_consecutive(data_nums):
        print(f"  {key}: {list(group)}")
    print()
