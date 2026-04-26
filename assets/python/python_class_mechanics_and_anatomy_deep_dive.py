"""Deep dive into Python class mechanics and anatomy.

This module demonstrates various aspects of Python classes, including basic
objects, structured classes, properties, access control, memory optimization
with slots, and dataclasses.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Any


# 1. The Fuzzy Object
class Option:
    """A simple class demonstrating a 'fuzzy' object with dynamic attributes."""


print("--- The Fuzzy Object ---")
my_option = Option()
my_option.strike = 100  # type: ignore[attr-defined]
my_option.expiry = "2025-12-20"  # type: ignore[attr-defined]
my_option.type = "Call"  # type: ignore[attr-defined]
print(f"Fuzzy Option strike: {my_option.strike}")  # type: ignore[attr-defined]


# 2. Structured Class - Base for further examples
class EuropeanOption:
    """A structured class representing a European option."""

    # Class Attributes
    CONTRACT_SIZE = 100
    _DEFAULT_OPTION_TYPE = "Call"  # Default for new options

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        """Initialize the EuropeanOption with strike, expiry, and type."""
        # Instance Attributes
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    def payoff(self, spot_price: float) -> float:
        """Calculate the payoff of the option at a given spot price."""
        if self.option_type == "Call":
            return max(spot_price - self.strike, 0.0)
        if self.option_type == "Put":
            return max(self.strike - spot_price, 0.0)
        msg = "Unknown option type"
        raise ValueError(msg)

    def __repr__(self) -> str:
        """Return a string representation of the EuropeanOption."""
        return (
            f"EuropeanOption(strike={self.strike}, "
            f"type='{self.option_type}', expiry='{self.expiry}')"
        )

    @classmethod
    def from_string(
        cls, description: str, expiry: str = "2025-12-20"
    ) -> EuropeanOption:
        """Create a EuropeanOption instance from a string description."""
        parts = description.split("-")
        option_type = parts[0]
        strike = float(parts[1])
        return cls(strike, expiry, option_type)

    @classmethod
    def set_default_option_type(cls, new_type: str) -> None:
        """Set a new default option type for the class."""
        if new_type not in {"Call", "Put"}:
            msg = "Option type must be 'Call' or 'Put'."
            raise ValueError(msg)
        cls._DEFAULT_OPTION_TYPE = new_type

    @staticmethod
    def d1(s: float, k: float, t: float, r: float, sigma: float) -> float:
        """Calculate the d1 component of the Black-Scholes formula."""
        return (math.log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))


# Usage examples - from initial setup
print("\n--- Structured Option ---")
euro_option = EuropeanOption(100.0, "2025-12-20", "Call")
print(euro_option)
print(f"Contract Size: {EuropeanOption.CONTRACT_SIZE}")

print(f"Payoff at 110: {euro_option.payoff(110)}")

# Factory usage
print("\n--- Factory Usage ---")
option_from_str = EuropeanOption.from_string("Put-120")
print(f"Created from string: {option_from_str}")

# Non-builder class method usage
print("\n--- Non-builder Class Method Usage ---")
# Accessing _DEFAULT_OPTION_TYPE is the point of the lesson.
print(f"Default option type before change: {EuropeanOption._DEFAULT_OPTION_TYPE}")  # noqa: SLF001
EuropeanOption.set_default_option_type("Put")
print(f"Default option type after change: {EuropeanOption._DEFAULT_OPTION_TYPE}")  # noqa: SLF001
EuropeanOption.set_default_option_type(
    "Call"
)  # Reset for consistency in following examples

# Static method usage
print("\n--- Static Method Usage ---")
d1_val = EuropeanOption.d1(s=100, k=100, t=1, r=0.05, sigma=0.2)
print(f"d1 value: {d1_val:.4f}")


# 3. Properties and Validation - using EuropeanOption as base
class EuropeanOptionWithProperty(EuropeanOption):
    """European option class with property-based validation for strike."""

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        """Initialize and trigger property validation."""
        # Assign to property to trigger validation
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    @property
    def strike(self) -> float:
        """Get the strike price."""
        return self._strike

    @strike.setter
    def strike(self, value: float) -> None:
        """Set the strike price with validation."""
        if value < 0:
            msg = "Strike price cannot be negative."
            raise ValueError(msg)
        self._strike = value


print("\n--- Property Validation (using EuropeanOptionWithProperty) ---")
opt_prop = EuropeanOptionWithProperty(100, "2025-12-20", "Call")
print(f"Current Strike: {opt_prop.strike}")

try:
    opt_prop.strike = -50
except ValueError as e:
    print(f"Expected Error caught: {e}")


# 4. Access Control - using EuropeanOption
class EuropeanOptionWithAccessControl(EuropeanOption):
    """European option class demonstrating access control (protected and private)."""

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        """Initialize with protected and private members."""
        super().__init__(strike, expiry, option_type)
        self._internal_cache: dict[str, Any] = {}  # Protected
        self.__secret_config = "confidential"  # noqa: S105


print("\n--- Access Control (using EuropeanOptionWithAccessControl) ---")
opt_access = EuropeanOptionWithAccessControl(100, "2025-12-20", "Call")
# Demonstrating access to protected/private members is the specific goal.
print(f"Protected access: {opt_access._internal_cache}")  # noqa: SLF001
try:
    print(opt_access.__secret_config)  # type: ignore[attr-defined] # noqa: SLF001
except AttributeError:
    print("Cannot access private variable directly.")
print(
    f"Mangled name access: {opt_access._EuropeanOptionWithAccessControl__secret_config}"  # noqa: SLF001
)


# 5. Memory Slots - comparing StandardOption (no slots) vs SlottedOption (with slots)
class StandardOption(EuropeanOption):
    """Standard option class without __slots__."""


class SlottedOption(EuropeanOption):
    """Option class using __slots__ for memory optimization."""

    __slots__ = ["expiry", "option_type", "strike"]  # Must match __init__ attributes

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        """Initialize the SlottedOption."""
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    # __repr__ is not inherited if slots are present, needs to be redefined
    def __repr__(self) -> str:
        """Return a string representation of the SlottedOption."""
        return (
            f"SlottedOption(strike={self.strike}, "
            f"type='{self.option_type}', expiry='{self.expiry}')"
        )


print("\n--- Memory Optimization (StandardOption vs SlottedOption) ---")
std_opt_mem = StandardOption(100, "2025-12-20", "Call")
slot_opt_mem = SlottedOption(100, "2025-12-20", "Call")


def get_size(obj: object) -> int:
    """Calculate the approximate memory size of an object."""
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


print(f"Standard Option Size: ~{get_size(std_opt_mem)} bytes")
print(f"Slotted Option Size:  ~{get_size(slot_opt_mem)} bytes")


# 6. Data Classes - using a simple OptionData
@dataclass
class OptionData:
    """A dataclass representing option data."""

    strike: float
    expiry: str
    option_type: str = "Call"


print("\n--- Data Classes ---")
opt_data = OptionData(100.0, "2025-12-20")
print(f"Dataclass: {opt_data}")
