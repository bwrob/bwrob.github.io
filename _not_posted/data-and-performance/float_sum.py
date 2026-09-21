import math
import time

import numpy as np
import pytest
from numba import njit


# --- 1. The Algorithm ---
@njit
def numba_bucket_sum(arr):
    OFFSET = 1100
    MAX_BUCKETS = 2200
    totals = np.zeros(MAX_BUCKETS, dtype=np.float64)
    compensations = np.zeros(MAX_BUCKETS, dtype=np.float64)

    for i in range(len(arr)):
        val = arr[i]
        if val == 0.0:
            continue

        _, exp = math.frexp(val)
        idx = exp + OFFSET

        t = totals[idx] + val
        if abs(totals[idx]) >= abs(val):
            compensations[idx] += (totals[idx] - t) + val
        else:
            compensations[idx] += (val - t) + totals[idx]
        totals[idx] = t

    final_total = 0.0
    final_comp = 0.0

    for i in range(MAX_BUCKETS):
        vals = (compensations[i], totals[i])
        for j in range(2):
            v = vals[j]
            if v == 0.0:
                continue
            t = final_total + v
            if abs(final_total) >= abs(v):
                final_comp += (final_total - t) + v
            else:
                final_comp += (v - t) + final_total
            final_total = t

    return final_total + final_comp


# --- 2. Data Generation Scenarios ---
N = 10_000_000


def generate_nasty_shuffle(n: int) -> np.ndarray:
    """The Nasty Shuffle.

    Mathematical Target: Left-to-right accumulator vulnerability.
    Description: Randomly distributes massive boundary numbers (+1e16 and -1e16)
    among millions of 1.0s.
    Expected Failure: A naive accumulator will absorb the 1e16, but once it does,
    adding 1.0 changes nothing because it falls off the edge of the 53-bit mantissa.
    The 1.0s are permanently swallowed before the accumulator encounters the -1e16
    to bring the magnitude back down.
    """
    arr = np.array([1e16] + [1.0] * n + [-1e16], dtype=np.float64)
    np.random.seed(42)
    np.random.shuffle(arr)
    return arr


def generate_sequential_avalanche(n: int) -> np.ndarray:
    """The Sequential Avalanche.

    Mathematical Target: Pairwise summation (NumPy) vulnerability.
    Description: Places +1e16 at the very beginning, followed sequentially by
    millions of 1.0s, ending with -1e16.
    Expected Failure: While pairwise algorithms survive the random shuffle,
    starting with 1e16 poisons the binary reduction tree instantly. The massive
    number acts like a disease, traveling up the tree and annihilating the 1.0s
    at every node before it finally meets its negative counterpart at the end.
    """
    return np.array([1e16] + [1.0] * n + [-1e16], dtype=np.float64)


def generate_micro_aggression(n: int) -> np.ndarray:
    """The Micro-Aggression.

    Mathematical Target: Precision degradation at the lowest bits.
    Description: Alternates between +1.0 and -1.0, interspersed with tiny
    fractions (1e-10).
    Expected Failure: Tests if algorithms lose lower-bound precision when
    constantly adding and subtracting whole integers. It forces the CPU to
    shift the bits of 1e-10 constantly, causing algorithms with poor error
    tracking to gradually bleed the true sum into floating-point noise.
    """
    arr = np.empty(n * 2, dtype=np.float64)
    arr[0::2] = 1.0 + 1e-10
    arr[1::2] = -1.0
    np.random.shuffle(arr)
    return arr


def generate_exponent_staircase() -> np.ndarray:
    """The Exponent Staircase.

    Mathematical Target: Extreme magnitude span and accumulator overflow.
    Description: Creates pairs of massive and tiny numbers spanning from
    10^100 down to 10^-100, alongside their exact negatives, and a small
    payload (3.14159).
    Expected Failure: Forces the accumulator to juggle a 200-order-of-magnitude
    spread simultaneously. Standard algorithms will overflow to infinity or
    completely obliterate the payload long before finding the negatives.
    """
    staircase = [10.0**i for i in range(-100, 100)] + [
        -(10.0**i) for i in range(-100, 100)
    ]
    staircase += [math.pi] * 1000
    arr = np.array(staircase, dtype=np.float64)
    np.random.shuffle(arr)
    return arr


def generate_subnormal_survivor() -> np.ndarray:
    """The Subnormal Survivor.

    Mathematical Target: Denormalized float handling (IEEE-754 subnormals).
    Description: Places a massive blockade (1e16), followed by the absolute
    smallest representable float in Python (5e-324), ending with -1e16.
    Expected Failure: Tests the raw exponent limits. If an algorithm uses
    naive magnitude mapping, it will underflow the subnormal number into an
    absolute zero, failing to preserve the mathematical payload.
    """
    arr = np.array([1e16] + [5e-324] * 1000 + [-1e16], dtype=np.float64)
    np.random.shuffle(arr)
    return arr


def generate_fractional_drift(n: int) -> np.ndarray:
    """The Fractional Drift.

    Mathematical Target: Accumulation of representation error.
    Description: Sums millions of 0.1s. Since 0.1 is an infinite repeating
    fraction in binary (0.000110011...), it cannot be represented perfectly.
    Expected Failure: Standard left-to-right accumulators will carry the
    tiny representation error forward, causing the final sum to drift
    significantly away from the true mathematical sum over millions of iterations.
    """
    return np.full(n, 0.1, dtype=np.float64)


def generate_kahan_killer(n: int) -> np.ndarray:
    """The Kahan Killer.

    Mathematical Target: Standard Kahan error-compensation failure.
    Description: Alternates between adding a tiny number (1e-10), a massive
    number (1e16), and the exact negative massive number (-1e16).
    Expected Failure: Standard Kahan summation assumes the running total is
    always larger than the incoming value. If the incoming value is larger,
    Kahan drops the error term into the void. This explicitly tests if our
    Neumaier-variant correctly checks magnitude before calculating compensation.
    """
    arr = np.empty(n, dtype=np.float64)
    arr[0::3] = 1e-10
    arr[1::3] = 1e16
    arr[2::3] = -1e16
    return arr


def generate_precision_annihilator(n: int) -> np.ndarray:
    """The Precision Annihilator.

    Mathematical Target: Catastrophic cancellation of the upper 52 bits.
    Description: Uses pairs of massive numbers that differ by exactly their
    Unit in the Last Place (ULP). At 1e16, the ULP is 2.0. We add (1e16 + 2.0),
    subtract 1e16, subtract 2.0, and add a tiny payload.
    Expected Failure: Tests precision retention when the top bits completely
    annihilate each other mid-calculation, forcing the accumulator to perfectly
    preserve the very last bit of the 53-bit mantissa alongside a tiny fraction.
    """
    arr = np.empty(n, dtype=np.float64)
    arr[0::4] = 1e16 + 2.0
    arr[1::4] = -1e16
    arr[2::4] = -2.0
    arr[3::4] = 1e-5
    np.random.shuffle(arr)
    return arr


def generate_sparse_mirage(n: int) -> np.ndarray:
    """The Sparse Mirage.

    Mathematical Target: Branch prediction and zero-skipping logic.
    Description: An array of 9.9 million exact zeros, with a few payloads
    sprinkled in.
    Expected Failure: This is purely a performance trap. Algorithms that
    blindly feed every number into their math functions (like calling math.frexp
    on 0.0) will waste massive amounts of CPU cycles. This tests the efficacy
    of the `if val == 0.0: continue` branch logic.
    """
    arr = np.zeros(n, dtype=np.float64)
    arr[::100000] = math.pi
    return arr


def generate_all_datasets():
    print("\n[Fixture] Generating datasets... This will take a moment.")
    return {
        "nasty_shuffle": generate_nasty_shuffle(N),
        "sequential_avalanche": generate_sequential_avalanche(N),
        "micro_aggression": generate_micro_aggression(N),
        "exponent_staircase": generate_exponent_staircase(),
        "subnormal_survivor": generate_subnormal_survivor(),
        "fractional_drift": generate_fractional_drift(N),
        "kahan_killer": generate_kahan_killer(N),
        "precision_annihilator": generate_precision_annihilator(N),
        "sparse_mirage": generate_sparse_mirage(N),
    }


# Global dictionary so pytest.mark.parametrize can read the keys
DATASETS = generate_all_datasets()


# --- 3. Pytest Fixtures & Setup ---
@pytest.fixture(scope="session", autouse=True)
def warmup_numba() -> None:
    """Force Numba to compile before tests start to avoid skewing test times."""
    _ = numba_bucket_sum(np.array([1.0, 2.0, -3.0], dtype=np.float64))


# --- 4. Accuracy Test Matrix ---
@pytest.mark.parametrize(
    ("algo_name", "algo_func"),
    [
        pytest.param(
            "builtin_sum",
            sum,
            marks=pytest.mark.xfail(
                reason="Standard accumulator fails catastrophic cancellation"
            ),
        ),
        pytest.param(
            "numpy_sum",
            np.sum,
            marks=pytest.mark.xfail(
                reason="Pairwise summation fails on large scale boundaries"
            ),
        ),
        pytest.param("numba_bucket", numba_bucket_sum),
    ],
)
@pytest.mark.parametrize("scenario", list(DATASETS.keys()))
def test_summation_accuracy(scenario, algo_name, algo_func) -> None:
    arr = DATASETS[scenario]

    # The Oracle: math.fsum guarantees mathematically perfect precision
    expected = math.fsum(arr)
    result = algo_func(arr)

    error = abs(expected - result)
    assert result == expected, (
        f"{algo_name} failed on {scenario}. Expected {expected}, got {result} (Error: {error})"
    )


# --- 5. Performance Test Matrix ---
@pytest.mark.parametrize("scenario", list(DATASETS.keys()))
def test_performance_vs_fsum(scenario) -> None:
    """Ensures that our Numba implementation is strictly faster than math.fsum
    across every single dataset configuration.
    Takes the best of 3 runs to avoid random OS CPU scheduling noise.
    """
    arr = DATASETS[scenario]

    def get_best_time(func, array, loops=3):
        best = float("inf")
        for _ in range(loops):
            start = time.perf_counter()
            func(array)
            elapsed = time.perf_counter() - start
            best = min(best, elapsed)
        return best

    time_fsum = get_best_time(math.fsum, arr)
    time_numba = get_best_time(numba_bucket_sum, arr)

    speed_factor = time_fsum / time_numba if time_numba > 0 else float("inf")

    # Assert that our custom compiled code beats Python's core C implementation
    assert time_numba < time_fsum, (
        f"[{scenario}] Numba ({time_numba:.4f}s) was NOT faster than fsum ({time_fsum:.4f}s)."
    )

    # Print the victory metrics for the pytest verbose (-s) output
    print(
        f"\n[Performance: {scenario}] Numba: {time_numba:.6f}s | math.fsum: {time_fsum:.6f}s"
    )
    print(f"[Performance: {scenario}] Numba was {speed_factor:.1f}x faster!")


if __name__ == "__main__":
    # Run the tests when the script is executed directly
    pytest.main([__file__, "-s"])
