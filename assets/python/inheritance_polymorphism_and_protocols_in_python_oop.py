"""Demonstration of inheritance, polymorphism, and protocols in Python.

This module covers Abstract Base Classes (ABCs), multiple inheritance,
mixins, composition, and structural subtyping using Protocols.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# --- 1. Abstract Base Classes ---

ZERO_THRESHOLD = 1e-9


class YieldCurve(ABC):
    """Abstract base class for all yield curves.

    Enforces that every subclass must implement `discount_factor`.
    """

    @abstractmethod
    def discount_factor(self, t: float) -> float:
        """Calculate discount factor D(t) for time t."""

    def zero_rate(self, t: float) -> float:
        """Calculate the zero rate for time t.

        Z(t) = -ln(D(t)) / t.
        """
        if t <= ZERO_THRESHOLD:  # Avoid division by zero
            return 0.0  # Approximation for t -> 0
        df = self.discount_factor(t)
        return -math.log(df) / t


# --- 2. Concrete Implementations ---


class FlatForwardCurve(YieldCurve):
    """Yield curve with a constant forward rate."""

    def __init__(self, rate: float) -> None:
        """Initialize the flat forward curve with a constant rate."""
        self.rate = rate

    def discount_factor(self, t: float) -> float:
        """Calculate the discount factor for a flat forward curve."""
        return math.exp(-self.rate * t)


# --- 3. Multiple Inheritance & Mixins ---


class SpreadMixin:
    """Mixin to add a spread to a curve.

    Must be mixed with a class that has a 'rate' attribute or similar logic,
    or we can override discount_factor calling super().
    """

    def __init__(self, spread: float, *args: object, **kwargs: object) -> None:
        """Initialize the spread mixin."""
        self.spread = spread
        super().__init__(*args, **kwargs)

    def discount_factor(self, t: float) -> float:
        """Calculate the discount factor including the spread."""
        # Get base discount factor from the parent class via MRO
        base_df = (
            super().discount_factor(t) if hasattr(super(), "discount_factor") else 1.0
        )
        # Apply spread discount: exp(-spread * t)
        return base_df * math.exp(-self.spread * t)


class ShiftedFlatCurve(SpreadMixin, FlatForwardCurve):
    """Inherit from both SpreadMixin and FlatForwardCurve.

    MRO (Method Resolution Order) ensures SpreadMixin.discount_factor is called first.
    """

    def __init__(self, rate: float, spread: float) -> None:
        """Initialize the shifted flat curve with rate and spread."""
        # Initialize both parents.
        # SpreadMixin.__init__ calls super().__init__, which goes to FlatForwardCurve
        super().__init__(spread=spread, rate=rate)


# --- 4. Interpolation Strategies (Composition vs Mixin) ---

# Approach A: Composition (Strategy Pattern)


class Interpolator(Protocol):
    """Protocol for interpolation strategies."""

    def interpolate(self, t: float, x: list[float], y: list[float]) -> float:
        """Interpolate y value for a given t."""
        ...


class LinearInterpolator:
    """Linear interpolation strategy."""

    def interpolate(self, t: float, x: list[float], y: list[float]) -> float:
        """Perform linear interpolation with flat extrapolation."""
        # Simple flat extrapolation for endpoints
        if t <= x[0]:
            return y[0]
        if t >= x[-1]:
            return y[-1]

        # Linear search (inefficient for large lists, but fine for demo)
        for i in range(len(x) - 1):
            if x[i] <= t <= x[i + 1]:
                t1, t2 = x[i], x[i + 1]
                y1, y2 = y[i], y[i + 1]
                w = (t - t1) / (t2 - t1)
                return (1 - w) * y1 + w * y2
        return y[-1]  # Should not happen


class InterpolatedZeroCurve(YieldCurve):
    """Yield curve that uses an interpolation strategy."""

    def __init__(
        self, times: list[float], rates: list[float], interpolator: Interpolator
    ) -> None:
        """Initialize with times, rates, and an interpolator."""
        if len(times) != len(rates):
            msg = "Times and rates must have same length"
            raise ValueError(msg)
        self.times = sorted(times)
        self.rates = [r for _, r in sorted(zip(times, rates, strict=False))]
        self.interpolator = interpolator

    def discount_factor(self, t: float) -> float:
        """Calculate discount factor using interpolated rate."""
        r = self.interpolator.interpolate(t, self.times, self.rates)
        return math.exp(-r * t)


# Approach B: Inheritance (Mixin)


class LinearInterpolationMixin:
    """Mixin that provides linear interpolation capability.

    Assumes the class has access to x and y data, passed as arguments.
    """

    def interpolate_linear(self, t: float, x: list[float], y: list[float]) -> float:
        """Perform linear interpolation."""
        if t <= x[0]:
            return y[0]
        if t >= x[-1]:
            return y[-1]

        for i in range(len(x) - 1):
            if x[i] <= t <= x[i + 1]:
                t1, t2 = x[i], x[i + 1]
                y1, y2 = y[i], y[i + 1]
                w = (t - t1) / (t2 - t1)
                return (1 - w) * y1 + w * y2
        return y[-1]


class MixinZeroCurve(LinearInterpolationMixin, YieldCurve):
    """Yield curve using a mixin for interpolation."""

    def __init__(self, times: list[float], rates: list[float]) -> None:
        """Initialize with times and rates."""
        self.times = sorted(times)
        self.rates = [r for _, r in sorted(zip(times, rates, strict=False))]

    def discount_factor(self, t: float) -> float:
        """Calculate discount factor using mixin interpolation."""
        # Use the method provided by the Mixin
        r = self.interpolate_linear(t, self.times, self.rates)
        return math.exp(-r * t)


# --- 5. Polymorphism ---


@dataclass
class CashFlow:
    """Represent a single cash flow at a specific time."""

    amount: float
    time: float


def price_bond(cashflows: list[CashFlow], curve: YieldCurve) -> float:
    """Polymorphic function: works with ANY instance of YieldCurve."""
    price = 0.0
    for cf in cashflows:
        price += cf.amount * curve.discount_factor(cf.time)
    return price


# --- 6. Protocols (Structural Subtyping) ---


@runtime_checkable
class Discountable(Protocol):
    """Define a 'shape' for objects that can provide a discount factor.

    Any class having this method is considered compatible, even if it
    doesn't inherit from Discountable.
    """

    def discount_factor(self, t: float) -> float:
        """Return the discount factor for time t."""
        ...


class SimpleDiscounter:
    """Class that satisfies the Discountable protocol without inheriting.

    This demonstrates structural subtyping.
    """

    def discount_factor(self, t: float) -> float:
        """Calculate discount factor using simple capitalization."""
        return 1 / (1 + 0.05 * t)  # Simple capitalization


def price_asset_structural(amount: float, t: float, model: Discountable) -> float:
    """Price an asset using any model that satisfies the Discountable protocol."""
    return amount * model.discount_factor(t)


# --- Usage ---

if __name__ == "__main__":
    # 1. ABC Usage
    flat_curve = FlatForwardCurve(rate=0.05)
    print(f"Flat Curve DF(1.0): {flat_curve.discount_factor(1.0):.4f}")

    # 2. Mixin (Spread) - Multiple Inheritance
    shifted = ShiftedFlatCurve(rate=0.05, spread=0.02)
    print(f"Shifted DF(1.0): {shifted.discount_factor(1.0):.4f}")

    # 3. Polymorphism (Composition)
    bond_cfs = [CashFlow(5, 1.0), CashFlow(105, 2.0)]

    # Use Strategy Pattern
    linear_interp = LinearInterpolator()
    curve_composition = InterpolatedZeroCurve(
        times=[0.5, 2.0], rates=[0.04, 0.06], interpolator=linear_interp
    )
    price_comp = price_bond(bond_cfs, curve_composition)
    print(f"Bond Price (Composition): {price_comp:.2f}")

    # Use Mixin for Interpolation
    curve_mixin = MixinZeroCurve(times=[0.5, 2.0], rates=[0.04, 0.06])
    price_mixin = price_bond(bond_cfs, curve_mixin)
    print(f"Bond Price (Mixin): {price_mixin:.2f}")

    # 4. Protocols
    simple = SimpleDiscounter()
    print(f"Is SimpleDiscounter a Discountable? {isinstance(simple, Discountable)}")
