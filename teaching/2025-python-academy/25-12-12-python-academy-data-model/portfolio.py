"""A module demonstrating the Python Data Model with a Portfolio class."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Position:
    """A financial position."""

    symbol: str
    value_usd: float


class Portfolio:
    """A collection of financial positions."""

    name: str
    managers: tuple[str, ...]

    def __init__(
        self,
        name: str,
        managers: tuple[str, ...],
        contents: list[Position] | None = None,
    ) -> None:
        """Initialize a new Portfolio.

        Args:
            name: The name of the portfolio.
            managers: A tuple of manager names.
            contents: A list of initial positions.

        """
        self.name = name
        self.managers = managers
        # Store positions in a dictionary keyed by symbol
        self._contents: dict[str, Position] = (
            {pos.symbol: pos for pos in contents} if contents else {}
        )

    def __add__(self, other: Portfolio) -> Portfolio:
        """Combine two portfolios."""
        if not isinstance(other, Portfolio):
            msg = (
                f"unsupported operand type(s) for +: '{type(self).__name__}' and "
                f"'{type(other).__name__}'"
            )
            raise TypeError(msg)

        new_name = f"{self.name} + {other.name}"
        new_managers = tuple(sorted(set(self.managers + other.managers)))

        # Merge contents
        all_positions = {}

        # Add positions from self
        for pos in self:
            all_positions[pos.symbol] = Position(pos.symbol, pos.value_usd)

        # Add positions from other
        for pos in other:
            if pos.symbol in all_positions:
                existing = all_positions[pos.symbol]
                existing.value_usd += pos.value_usd
            else:
                all_positions[pos.symbol] = Position(pos.symbol, pos.value_usd)

        return Portfolio(new_name, new_managers, list(all_positions.values()))

    def __len__(self) -> int:
        """Return the number of positions in the portfolio."""
        return len(self._contents)

    def __getitem__(self, symbol: str) -> Position | None:
        """Retrieve a position by its symbol."""
        return self._contents.get(symbol)

    def __iter__(self) -> Iterator[Position]:
        """Iterate over the positions in the portfolio."""
        return iter(self._contents.values())

    def __contains__(self, item: str | Position) -> bool:
        """Check if a symbol or position is in the portfolio."""
        if isinstance(item, str):
            return item in self._contents
        if isinstance(item, Position):
            return item.symbol in self._contents
        return False

    def __bool__(self) -> bool:
        """Return True if the portfolio has positions, False otherwise."""
        return bool(self._contents)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"Portfolio(name={self.name!r}, managers={self.managers!r}, "
            f"contents={list(self._contents.values())!r})"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return (
            f"Portfolio '{self.name}' with {len(self)} positions managed by "
            f"{', '.join(self.managers)}"
        )

    def total_value(self) -> float:
        """Calculate the total USD value of the portfolio."""
        return sum(pos.value_usd for pos in self)


if __name__ == "__main__":
    # Create some positions
    pos1 = Position("AAPL", 15000.0)
    pos2 = Position("GOOG", 140000.0)
    pos3 = Position("TSLA", 18000.0)
    pos4 = Position("MSFT", 30000.0)
    pos5 = Position("AAPL", 8000.0)  # More AAPL value

    # Create portfolios
    p1 = Portfolio("Tech Growth", ("Alice", "Bob"), [pos1, pos2, pos3])
    p2 = Portfolio("Safe Haven", ("Bob", "Charlie"), [pos4, pos5])
    empty_p = Portfolio("Empty", ("Dave",))

    # 1. __len__
    print(f"Number of positions in p1: {len(p1)}")

    # 2. __getitem__ (Symbol lookup)
    aapl_pos = p1["AAPL"]
    if aapl_pos:
        print(f"AAPL position found in p1: {aapl_pos}")
    else:
        print("AAPL position not found in p1.")

    # 3. Iteration
    print("Positions in p1:")
    for pos in p1:
        print(f" - {pos.symbol}: ${pos.value_usd:,.2f}")

    # 4. __contains__
    print(f"Is 'AAPL' in p1? {'AAPL' in p1}")
    print(f"Is pos4 (MSFT) in p1? {pos4 in p1}")

    # 5. __bool__
    print(f"Is p1 truthy? {bool(p1)}")
    print(f"Is empty_p truthy? {bool(empty_p)}")

    # 6. __add__
    p3 = p1 + p2
    print("\n--- Merged Portfolio (p1 + p2) ---")
    print(p3)
    print(f"Managers: {p3.managers}")
    print("Positions:")
    for pos in p3:
        print(f" - {pos.symbol}: Value=${pos.value_usd:,.2f}")

    print(f"Total Portfolio Value: ${p3.total_value():,.2f}")
