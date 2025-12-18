from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import math

# --- 1. Abstract Base Classes ---


class YieldCurve(ABC):
    """
    Abstract base class for all yield curves.
    Enforces that every subclass must implement `discount_factor`.
    """

    @abstractmethod
    def discount_factor(self, t: float) -> float:
        """Calculate discount factor D(t) for time t."""
        pass

    def zero_rate(self, t: float) -> float:
        """
        Concrete method shared by all curves.
        Z(t) = -ln(D(t)) / t
        """
        if t <= 1e-9:  # Avoid division by zero
            return 0.0  # Approximation for t -> 0
        df = self.discount_factor(t)
        return -math.log(df) / t


# --- 2. Concrete Implementations ---


class FlatForwardCurve(YieldCurve):
    def __init__(self, rate: float):
        self.rate = rate

    def discount_factor(self, t: float) -> float:
        return math.exp(-self.rate * t)


# --- 3. Multiple Inheritance & Mixins ---


class SpreadMixin:
    """
    Mixin to add a spread to a curve.
    Must be mixed with a class that has a 'rate' attribute or similar logic,
    or we can override discount_factor calling super().
    """

    def __init__(self, spread: float, *args, **kwargs):
        self.spread = spread
        super().__init__(*args, **kwargs)

    def discount_factor(self, t: float) -> float:
        # Get base discount factor
        base_df = super().discount_factor(t)
        # Apply spread discount: exp(-spread * t)
        return base_df * math.exp(-self.spread * t)


class ShiftedFlatCurve(SpreadMixin, FlatForwardCurve):
    """
    Inherits from both SpreadMixin and FlatForwardCurve.
    MRO (Method Resolution Order) ensures SpreadMixin.discount_factor is called first.
    """

    def __init__(self, rate: float, spread: float):
        # Initialize both parents.
        # SpreadMixin.__init__ calls super().__init__, which goes to FlatForwardCurve
        super().__init__(spread=spread, rate=rate)


# --- 4. Interpolation Strategies (Composition vs Mixin) ---

# Approach A: Composition (Strategy Pattern)


class Interpolator(Protocol):
    def interpolate(self, t: float, x: list[float], y: list[float]) -> float: ...


class LinearInterpolator:
    def interpolate(self, t: float, x: list[float], y: list[float]) -> float:
        # Simple flat extrapolation for endpoints
        if t <= x[0]:
            return y[0]
        elif t >= x[-1]:
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
    def __init__(
        self, times: list[float], rates: list[float], interpolator: Interpolator
    ):
        if len(times) != len(rates):
            raise ValueError("Times and rates must have same length")
        self.times = sorted(times)
        self.rates = [r for _, r in sorted(zip(times, rates))]
        self.interpolator = interpolator

    def discount_factor(self, t: float) -> float:
        r = self.interpolator.interpolate(t, self.times, self.rates)
        return math.exp(-r * t)


# Approach B: Inheritance (Mixin)


class LinearInterpolationMixin:
    """
    Mixin that provides linear interpolation capability.
    Assumes the class has access to x and y data, passed as arguments.
    """

    def interpolate_linear(self, t: float, x: list[float], y: list[float]) -> float:
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
    def __init__(self, times: list[float], rates: list[float]):
        self.times = sorted(times)
        self.rates = [r for _, r in sorted(zip(times, rates))]

    def discount_factor(self, t: float) -> float:
        # Use the method provided by the Mixin
        r = self.interpolate_linear(t, self.times, self.rates)
        return math.exp(-r * t)


# --- 5. Polymorphism ---


@dataclass
class CashFlow:
    amount: float
    time: float


def price_bond(cashflows: list[CashFlow], curve: YieldCurve) -> float:
    """
    Polymorphic function: works with ANY instance of YieldCurve.
    """
    price = 0.0
    for cf in cashflows:
        price += cf.amount * curve.discount_factor(cf.time)
    return price


# --- 6. Protocols (Structural Subtyping) ---


@runtime_checkable
class Discountable(Protocol):
    """
    A Protocol defines a 'shape'. Any class having this method
    is considered compatible, even if it doesn't inherit from Discountable.
    """

    def discount_factor(self, t: float) -> float: ...


class SimpleDiscounter:
    """
    This class does NOT inherit from YieldCurve,
    but it satisfies the Discountable protocol.
    """

    def discount_factor(self, t: float) -> float:
        return 1 / (1 + 0.05 * t)  # Simple capitalization


def price_asset_structural(amount: float, t: float, model: Discountable) -> float:
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
