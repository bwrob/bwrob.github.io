
import pathlib
from functools import partial


def countdown(n):
    while True:
        yield n
        n -= 1


list(iter(countdown(10).__next__, 0))


class countdown:
    def __init__(self, value) -> None:
        self._value = value

    def __call__(self):
         self._value -= 1
         return self._value


list(iter(countdown(10), 0))


with pathlib.Path("mydata.db").open("rb") as f:
    for block in iter(partial(f.read, 64), b""):
        process_block(block)
