import itertools
import random
import tracemalloc
from dataclasses import dataclass
from datetime import date
from functools import wraps

# --- Lists vs. Tuples ---
print("--- Lists vs. Tuples ---")
my_list = [i for i in range(1_000_000)]
# This creates a list with 1,000,000 integers in memory.
print(f"my_list created with {len(my_list)} elements.")


# --- Iterators ---
print("\n--- Iterators ---")
my_list_iterator = [1, 2, 3]
my_iterator = iter(my_list_iterator)

print(next(my_iterator))
print(next(my_iterator))
print(next(my_iterator))


# --- Generators ---
print("\n--- Generators ---")


def number_generator(n):
    for i in range(n):
        yield i


gen = number_generator(1_000_000)
print("Generator created.")

# --- Example: Flattening a List of Lists ---
print("\n--- Example: Flattening a List of Lists ---")
trades_cashflows = [
    [10, 20, 30],
    [15, 25],
    [100, -10, 5],
    110,
]


def flatten(list_of_lists):
    for item in list_of_lists:
        if isinstance(item, list):
            for subitem in item:
                yield subitem
        else:
            yield item


all_cashflows_generator = flatten(trades_cashflows)

for cf in all_cashflows_generator:
    print(cf, end=" ")
print("\n")


# --- Memory Efficiency in Action ---
print("--- Memory Efficiency in Action ---")


def profile_memory(func):
    """A decorator to profile the memory usage of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        print(f"Function: {func.__name__}")
        print(
            f"Current memory usage is {current / 10**6:.6f}MB; Peak was {peak / 10**6:.6f}MB"
        )
        tracemalloc.stop()
        return result

    return wrapper


@profile_memory
def create_list(n):
    """This function creates a list of n numbers."""
    return [i for i in range(n)]


@profile_memory
def create_generator(n):
    """This function creates a generator of n numbers."""
    return (i for i in range(n))


n = 1_000_000
print("Profiling memory for list creation...")
my_list = create_list(n)

print("\nProfiling memory for generator creation...")
my_generator = create_generator(n)


@profile_memory
def consume_generator(gen):
    return list(gen)


print("\nProfiling memory for generator consumption...")
consumed_list = consume_generator(my_generator)
print("\n")


# --- Essential Iteration Tools: enumerate ---
print("--- Essential Iteration Tools: enumerate ---")
cashflows = [100, 100, 100, 1100]
for period, cf in enumerate(cashflows, 1):
    print(f"Period {period}: Cashflow = {cf}")
print("\n")


# --- Essential Iteration Tools: zip ---
print("--- Essential Iteration Tools: zip ---")
trade_dates = ["2025-11-05", "2025-11-06", "2025-11-07"]
notionals = [1_000_000, 2_500_000, 500_000]
for trade_date, notional in zip(trade_dates, notionals, strict=False):
    print(f"On {trade_date}, we traded a notional of {notional:,}")
print("\n")


# --- Essential Iteration Tools: sorted ---
print("--- Essential Iteration Tools: sorted ---")


@dataclass
class Trade:
    trade_id: str
    maturity: date
    notional: float


trades = [
    Trade("T1", date(2026, 12, 31), 10_000_000),
    Trade("T2", date(2025, 12, 31), 5_000_000),
    Trade("T3", date(2027, 12, 31), 15_000_000),
]

sorted_by_maturity = sorted(trades, key=lambda t: t.maturity)
for trade in sorted_by_maturity:
    print(trade)
print("\n")


# --- The itertools Module: chain.from_iterable ---
print("--- The itertools Module: chain.from_iterable ---")
fixed_leg = [50, 50, 50, 50]
floating_leg = [50 + random.uniform(-5, 5) for _ in range(6)]
bond_legs = [fixed_leg, floating_leg]
full_swap_leg = itertools.chain.from_iterable(bond_legs)

print("Full cashflow stream for the leg:")
for cf in full_swap_leg:
    print(f"{cf:.2f}", end=" ")
print("\n")


# --- The itertools Module: accumulate (P&L) ---
print("--- The itertools Module: accumulate (P&L) ---")
daily_pnl = [150, -200, 50, 300, -100]
cumulative_pnl = itertools.accumulate(daily_pnl)
print(list(cumulative_pnl))
print("\n")


# --- The itertools Module: accumulate (Amortization) ---
print("--- The itertools Module: accumulate (Amortization) ---")


def outstanding_balance(balance, payment, rate):
    return balance * (1 + rate) - payment


initial_notional = 1_000_000
interest_rate = 0.01
monthly_payment = 5000
payments = itertools.repeat(monthly_payment)

balances = itertools.accumulate(
    payments,
    lambda balance, pmt: outstanding_balance(balance, pmt, interest_rate),
    initial=initial_notional,
)

amortization_schedule = itertools.takewhile(lambda balance: balance > 0, balances)

for i, balance in enumerate(amortization_schedule):
    print(f"Month {i + 1}: {balance:,.2f}")
print("\n")


# --- The itertools Module: pairwise ---
print("--- The itertools Module: pairwise ---")
payment_dates = [date(2025, 1, 15), date(2025, 7, 15), date(2026, 1, 15)]


def year_fraction(start, end):
    return (end - start).days / 365.25


for start, end in itertools.pairwise(payment_dates):
    yf = year_fraction(start, end)
    print(f"Period: {start} to {end}, Year Fraction: {yf:.4f}")
print("\n")


# --- The itertools Module: cycle ---
print("--- The itertools Module: cycle ---")
scenarios = itertools.cycle(["Base", "Rate Up", "Rate Down"])
for _ in range(5):
    print(f"Running scenario: {next(scenarios)}")
