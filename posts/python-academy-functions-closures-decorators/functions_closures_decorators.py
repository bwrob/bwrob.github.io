import time
from collections.abc import Callable


# Functions
def fibonacci_iterative(n: int) -> int:
    """Calculate the nth Fibonacci number using an iterative approach."""
    if n < 0:
        msg = "Fibonacci is not defined for negative numbers."
        raise ValueError(msg)
    if n < 2:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


print(fibonacci_iterative.__doc__)
print(fibonacci_iterative.__name__)

isinstance(fibonacci_iterative, object)


# Benchmarking Fibonacci Implementations
def fibonacci_recursive(n: int) -> int:
    """Calculate the nth Fibonacci number using a recursive approach."""
    if n < 0:
        msg = "Fibonacci is not defined for negative numbers."
        raise ValueError(msg)
    if n < 2:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


FIBONACCI_CACHE: dict[int, int] = {}


def fibonacci_recursive_cached(n: int) -> int:
    """Calculate the nth Fibonacci number using recursion with memoization."""
    if n < 0:
        msg = "Fibonacci is not defined for negative numbers."
        raise ValueError(msg)
    if n < 2:
        return n

    if n in FIBONACCI_CACHE:
        return FIBONACCI_CACHE[n]

    result = fibonacci_recursive_cached(n - 1) + fibonacci_recursive_cached(n - 2)

    FIBONACCI_CACHE[n] = result
    return result


def benchmark(functions: list[Callable[[int], int]], n: int) -> None:
    """Benchmarks a list of functions."""
    for func in functions:
        start = time.perf_counter()
        func(n)
        end = time.perf_counter()
        print(f"Function {func.__name__} took {end - start:.6f} seconds.")


fib_functions = [fibonacci_recursive, fibonacci_recursive_cached, fibonacci_iterative]
benchmark(fib_functions, 30)


# Closures
def get_greeter(greeting: str) -> Callable:
    """Returns a greeter function."""

    def greeter(name: str) -> str:
        return f"{greeting}, {name}!"

    return greeter


good_morning_greeter = get_greeter("Good morning")
print(good_morning_greeter("World"))

good_morning_greeter.__closure__[0].cell_contents


def polynomial_factory(coefficients: tuple[float, ...]) -> callable:
    """A factory that creates a polynomial function from a tuple of coefficients.
    The coefficients are ordered from the highest power to the lowest.
    """

    def polynomial(x: float) -> float:
        """Evaluates the polynomial for a given x."""
        return sum(c * (x**i) for i, c in enumerate(reversed(coefficients)))

    return polynomial


# P(x) = 2x^2 + 3x + 5
p1 = polynomial_factory((2, 3, 5))

# Q(x) = x^3 - 8
p2 = polynomial_factory((1, 0, 0, -8))

print(p1(5))
print(p2(5))


# Decorators
def my_cache(func: Callable) -> Callable:
    """A simple cache decorator."""
    _cache = {}

    def wrapper(*args):
        if args in _cache:
            return _cache[args]
        result = func(*args)
        _cache[args] = result
        return result

    return wrapper


@my_cache
def fibonacci_cached_by_me(n: int) -> int:
    """Calculate the nth Fibonacci number using recursion with our own cache decorator."""
    if n < 0:
        msg = "Fibonacci is not defined for negative numbers."
        raise ValueError(msg)
    if n < 2:
        return n
    return fibonacci_cached_by_me(n - 1) + fibonacci_cached_by_me(n - 2)


fibonacci_cached_by_me(30)


def repeat(times: int) -> Callable:
    """A decorator that repeats a function call a given number of times."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def say_hello(name: str) -> None:
    print(f"Hello, {name}!")


say_hello("World")
