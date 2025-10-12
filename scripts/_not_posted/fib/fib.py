from time import perf_counter


def print_time(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"Czas wykonania funkcji {func.__name__}: {end-start}")
        return result

    return wrapper


def append_time(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"Czas wykonania funkcji {func.__name__}: {end-start}")
        return (*args, result, end - start)

    return wrapper


@append_time
def fib_rekurencja(n):
    if n < 2:
        return n
    return fib_rekurencja(n - 1) + fib_rekurencja(n - 2)


def fib_iteracyjnie(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


if __name__ == "__main__":
    n = 6
    print(fib_iteracyjnie(n))
    print(fib_rekurencja(n))

    # pyinstrument --renderer=html --interval=0.0000000000000000000000001 fib.py
