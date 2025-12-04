import math
import sys


# 1. The Fuzzy Object
class Option:
    pass


print("--- The Fuzzy Object ---")
my_option = Option()
my_option.strike = 100
my_option.expiry = "2025-12-20"
my_option.type = "Call"
print(f"Fuzzy Option strike: {my_option.strike}")


# 2. Structured Class
class EuropeanOption:
    # Class Attribute
    CONTRACT_SIZE = 100

    def __init__(self, strike: float, expiry: str, option_type: str):
        # Instance Attributes
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type

    def payoff(self, spot_price: float) -> float:
        """Instance Method"""
        if self.option_type == "Call":
            return max(spot_price - self.strike, 0.0)
        elif self.option_type == "Put":
            return max(self.strike - spot_price, 0.0)
        else:
            raise ValueError("Unknown option type")

    def __repr__(self):
        return f"EuropeanOption(strike={self.strike}, type='{self.option_type}', expiry='{self.expiry}')"

    @classmethod
    def from_string(cls, description: str, expiry: str = "2025-12-20"):
        """Class Method (Factory)"""
        # Parses strings like "Call-100"
        parts = description.split("-")
        option_type = parts[0]
        strike = float(parts[1])
        return cls(strike, expiry, option_type)

    @staticmethod
    def d1(S, K, T, r, sigma):
        """Static Method"""
        return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


# Usage examples
print("\n--- Structured Option ---")
euro_option = EuropeanOption(100.0, "2025-12-20", "Call")
print(euro_option)
print(f"Contract Size: {EuropeanOption.CONTRACT_SIZE}")

print(f"Payoff at 110: {euro_option.payoff(110)}")

# Factory usage
print("\n--- Factory Usage ---")
option_from_str = EuropeanOption.from_string("Put-120")
print(f"Created from string: {option_from_str}")

# Static method usage
print("\n--- Static Method Usage ---")
d1_val = EuropeanOption.d1(S=100, K=100, T=1, r=0.05, sigma=0.2)
print(f"d1 value: {d1_val:.4f}")


# 3. Properties and Validation
class ValidatedOption:
    def __init__(self, strike: float):
        self.strike = strike  # Triggers the setter

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value):
        if value < 0:
            raise ValueError("Strike price cannot be negative.")
        self._strike = value


print("\n--- Property Validation ---")
opt = ValidatedOption(100)
print(f"Current Strike: {opt.strike}")
try:
    opt.strike = -50
except ValueError as e:
    print(f"Expected Error caught: {e}")


# 4. Access Control
class Model:
    def __init__(self):
        self._calibration_date = "2025-01-01"  # Protected
        self.__algorithm_secret = 42  # Private


print("\n--- Access Control ---")
model = Model()
print(f"Protected access: {model._calibration_date}")
try:
    print(model.__algorithm_secret)
except AttributeError:
    print("Cannot access private variable directly.")
print(f"Mangled name access: {model._Model__algorithm_secret}")


# 5. Memory Slots
class StandardTick:
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price


class SlottedTick:
    __slots__ = ["symbol", "price"]

    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price


print("\n--- Memory Optimization ---")
tick_std = StandardTick("AAPL", 150.0)
tick_slot = SlottedTick("AAPL", 150.0)


def get_size(obj):
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


print(f"Standard Tick Size: ~{get_size(tick_std)} bytes")
print(f"Slotted Tick Size:  ~{get_size(tick_slot)} bytes")
