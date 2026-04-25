import math
import sys
from dataclasses import dataclass


# 1. The Fuzzy Object
class Option:
    pass


print("--- The Fuzzy Object ---")
my_option = Option()
my_option.strike = 100
my_option.expiry = "2025-12-20"
my_option.type = "Call"
print(f"Fuzzy Option strike: {my_option.strike}")


# 2. Structured Class - Base for further examples
class EuropeanOption:
    # Class Attributes
    CONTRACT_SIZE = 100
    _DEFAULT_OPTION_TYPE = "Call"  # Default for new options

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        # Instance Attributes
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    def payoff(self, spot_price: float) -> float:
        """Instance Method."""
        if self.option_type == "Call":
            return max(spot_price - self.strike, 0.0)
        if self.option_type == "Put":
            return max(
                self.strike - spot_price, 0.0
            )  # Should be self.strike - spot_price
        msg = "Unknown option type"
        raise ValueError(msg)

    def __repr__(self) -> str:
        return f"EuropeanOption(strike={self.strike}, type='{self.option_type}', expiry='{self.expiry}')"

    @classmethod
    def from_string(cls, description: str, expiry: str = "2025-12-20"):
        """Class Method (Factory)."""
        parts = description.split("-")
        option_type = parts[0]
        strike = float(parts[1])
        return cls(strike, expiry, option_type)

    @classmethod
    def set_default_option_type(cls, new_type: str) -> None:
        """Sets a new default option type for the class."""
        if new_type not in {"Call", "Put"}:
            msg = "Option type must be 'Call' or 'Put'."
            raise ValueError(msg)
        cls._DEFAULT_OPTION_TYPE = new_type

    @staticmethod
    def d1(S, K, T, r, sigma):
        """Static Method."""
        return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


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
print(f"Default option type before change: {EuropeanOption._DEFAULT_OPTION_TYPE}")
EuropeanOption.set_default_option_type("Put")
print(f"Default option type after change: {EuropeanOption._DEFAULT_OPTION_TYPE}")
EuropeanOption.set_default_option_type(
    "Call"
)  # Reset for consistency in following examples

# Static method usage
print("\n--- Static Method Usage ---")
d1_val = EuropeanOption.d1(S=100, K=100, T=1, r=0.05, sigma=0.2)
print(f"d1 value: {d1_val:.4f}")


# 3. Properties and Validation - using EuropeanOption as base
class EuropeanOptionWithProperty(EuropeanOption):
    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        # Assign to property to trigger validation
        self.strike = strike
        self.expiry = expiry  # Will need to adjust parent __init__ for this
        self.option_type = option_type

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value) -> None:
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
    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        super().__init__(strike, expiry, option_type)
        self._internal_cache = {}  # Protected
        self.__secret_config = "confidential"  # Private


print("\n--- Access Control (using EuropeanOptionWithAccessControl) ---")
opt_access = EuropeanOptionWithAccessControl(100, "2025-12-20", "Call")
print(f"Protected access: {opt_access._internal_cache}")
try:
    print(opt_access.__secret_config)
except AttributeError:
    print("Cannot access private variable directly.")
print(
    f"Mangled name access: {opt_access._EuropeanOptionWithAccessControl__secret_config}"
)


# 5. Memory Slots - comparing StandardOption (no slots) vs SlottedOption (with slots)
class StandardOption(EuropeanOption):
    # No __slots__
    pass


class SlottedOption(EuropeanOption):
    __slots__ = ["expiry", "option_type", "strike"]  # Must match __init__ attributes

    def __init__(self, strike: float, expiry: str, option_type: str) -> None:
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    # __repr__ is not inherited if slots are present, needs to be redefined or use parent
    def __repr__(self) -> str:
        return f"SlottedOption(strike={self.strike}, type='{self.option_type}', expiry='{self.expiry}')"


print("\n--- Memory Optimization (StandardOption vs SlottedOption) ---")
std_opt_mem = StandardOption(100, "2025-12-20", "Call")
slot_opt_mem = SlottedOption(100, "2025-12-20", "Call")


def get_size(obj):
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


print(f"Standard Option Size: ~{get_size(std_opt_mem)} bytes")
print(f"Slotted Option Size:  ~{get_size(slot_opt_mem)} bytes")


# 6. Data Classes - using a simple OptionData
@dataclass
class OptionData:
    strike: float
    expiry: str
    option_type: str = "Call"


print("\n--- Data Classes ---")
opt_data = OptionData(100.0, "2025-12-20")
print(f"Dataclass: {opt_data}")
