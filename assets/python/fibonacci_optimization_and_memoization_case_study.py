"""A collection of functions to calculate Fibonacci numbers."""

from functools import lru_cache

from rich.console import Console
from rich.tree import Tree

__ERROR_MSG_NEGATIVE = "Fibonacci is not defined for negative numbers."
FIB_THRESHOLD = 2


def fibonacci_recursive(n: int) -> int:
    """Calculate the nth Fibonacci number using a recursive approach."""
    if n < 0:
        raise ValueError(__ERROR_MSG_NEGATIVE)
    if n < FIB_THRESHOLD:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_recursive_talkative(n: int) -> int:
    """Calculate the nth Fibonacci number using a recursive approach."""
    tree = Tree(f"fibonacci_recursive_talkative({n})")

    def worker(n: int, tree: Tree) -> int:
        """Calculate the nth Fibonacci number using a recursive approach."""
        node = tree.add(f"fibonacci_recursive({n}) called")
        if n < 0:
            raise ValueError(__ERROR_MSG_NEGATIVE)
        if n < FIB_THRESHOLD:
            return n
        return worker(n - 1, node) + worker(n - 2, node)

    result = worker(n, tree)
    Console().print(tree)
    return result


__CACHE: dict[int, int] = {}


def fibonacci_recursive_cached(n: int) -> int:
    """Calculate the nth Fibonacci number using recursion with memoization."""
    if n < 0:
        raise ValueError(__ERROR_MSG_NEGATIVE)
    if n < FIB_THRESHOLD:
        return n

    if n in __CACHE:
        return __CACHE[n]
    __CACHE[n] = fibonacci_recursive_cached(n - 1) + fibonacci_recursive_cached(n - 2)

    return __CACHE[n]


@lru_cache
def fibonacci_recursive_cached_lru(n: int) -> int:
    """Calculate the nth Fibonacci number using recursion with memoization."""
    if n < 0:
        raise ValueError(__ERROR_MSG_NEGATIVE)
    if n < FIB_THRESHOLD:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_iterative(n: int) -> int:
    """Calculate the nth Fibonacci number using an iterative approach."""
    if n < 0:
        raise ValueError(__ERROR_MSG_NEGATIVE)
    if n < FIB_THRESHOLD:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    N = 10

    print(f"Calculating Fibonacci numbers up to {N}:")

    print("\nIterative approach:")
    for i in range(N + 1):
        result = fibonacci_iterative(i)
        print(f"fib({i}) = {result}")

    print("\nRecursive approach:")
    for i in range(N + 1):
        result = fibonacci_recursive(i)
        print(f"fib({i}) = {result}")

    print("\nRecursive approach with caching (manual):")
    for i in range(N + 1):
        result = fibonacci_recursive_cached(i)
        print(f"fib({i}) = {result}")

    talkative_result = fibonacci_recursive_talkative(5)
