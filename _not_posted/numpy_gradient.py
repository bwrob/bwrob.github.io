import time

import jax
import jax.numpy as jnp
import numpy as np
import scipy.ndimage
from numba import float64, guvectorize, njit, stencil

# ==========================================
# 1. Optimized Derivative Functions
# ==========================================


def deriv_gradient(y, dx):
    return np.gradient(y, dx)


def deriv_convolve(y, dx):
    inv_2dx = 0.5 / dx
    kernel = np.array([1.0, 0.0, -1.0]) * inv_2dx
    return np.convolve(y, kernel, mode="same")


def deriv_slicing(y, dx):
    out = np.empty_like(y)

    inv_dx = 1.0 / dx
    inv_2dx = 0.5 / dx

    out[1:-1] = (y[2:] - y[:-2]) * inv_2dx
    out[0] = (y[1] - y[0]) * inv_dx
    out[-1] = (y[-1] - y[-2]) * inv_dx

    return out


@njit()
def deriv_numba(y, dx):
    n = len(y)
    out = np.empty(n, dtype=y.dtype)

    inv_dx = 1.0 / dx
    inv_2dx = 0.5 / dx

    out[0] = (y[1] - y[0]) * inv_dx
    out[n - 1] = (y[n - 1] - y[n - 2]) * inv_dx

    for i in range(1, n - 1):
        out[i] = (y[i + 1] - y[i - 1]) * inv_2dx

    return out


@guvectorize(
    [(float64[:], float64, float64[:])],
    "(n),()->(n)",
    nopython=True,
    fastmath=True,
    target="parallel",
)
def deriv_numba_guvec(y, dx, out):
    n = y.shape[0]
    inv_dx = 1.0 / dx
    inv_2dx = 0.5 / dx
    if n > 1:
        out[0] = (y[1] - y[0]) * inv_dx
        out[n - 1] = (y[n - 1] - y[n - 2]) * inv_dx
        for i in range(1, n - 1):
            out[i] = (y[i + 1] - y[i - 1]) * inv_2dx


# --- NEW: Numba Stencil ---


# Define the kernel using relative indexing
@stencil
def _stencil_kernel(y, inv_2dx):
    return (y[1] - y[-1]) * inv_2dx


@njit(fastmath=True)
def deriv_numba_stencil(y, dx):
    """Applies the stencil and manually fixes the boundary conditions."""
    inv_dx = 1.0 / dx
    inv_2dx = 0.5 / dx

    # Numba stencil creates the output array automatically
    out = _stencil_kernel(y, inv_2dx)

    # Fix the edges (stencil leaves them as 0 by default)
    out[0] = (y[1] - y[0]) * inv_dx
    out[-1] = (y[-1] - y[-2]) * inv_dx
    return out


# --- JAX & SciPy ---


@jax.jit
def _deriv_jax_slicing(y, dx):
    inv_dx = 1.0 / dx
    inv_2dx = 0.5 / dx
    left = jnp.array([(y[1] - y[0]) * inv_dx])
    middle = (y[2:] - y[:-2]) * inv_2dx
    right = jnp.array([(y[-1] - y[-2]) * inv_dx])
    return jnp.concatenate((left, middle, right))


def deriv_jax(y, dx):
    return _deriv_jax_slicing(y, dx).block_until_ready()


def deriv_scipy(y, dx):
    inv_2dx = 0.5 / dx
    weights = np.array([1.0, 0.0, -1.0]) * inv_2dx
    return scipy.ndimage.convolve1d(y, weights, mode="constant", cval=0.0)


# ==========================================
# 2. Benchmarking Setup
# ==========================================


def run_benchmark():
    print("Generating data (10,000,000 points)...")
    n_points = 100_000_000
    dx = 0.001
    x = np.arange(n_points) * dx
    y = np.sin(x)

    print("Moving data to JAX...")
    y_jax = jnp.array(y)

    print("Warming up compilers (Numba & JAX)...")
    warmup_arr = np.array([1.0, 2.0, 3.0, 4.0])
    _ = deriv_numba(warmup_arr, dx)
    _ = deriv_numba_guvec(warmup_arr, dx)
    _ = deriv_numba_stencil(warmup_arr, dx)  # Warm up Stencil
    _ = deriv_jax(jnp.array(warmup_arr), dx)
    _ = deriv_scipy(warmup_arr, dx)
    _ = deriv_convolve(warmup_arr, dx)

    methods = {
        "Numba GuVec (Parallel)": deriv_numba_guvec,
        "Numba Stencil": deriv_numba_stencil,
        "Numba JIT Loop": deriv_numba,
        "JAX JIT Slicing": deriv_jax,
        "NumPy Slicing": deriv_slicing,
        "NumPy Gradient": deriv_gradient,
        "SciPy Convolve1D": deriv_scipy,
        "NumPy Convolve": deriv_convolve,
    }

    results = {}
    iterations = 100

    print(f"\nRunning benchmark ({iterations} iterations each)...\n")
    print(f"{'Method':<25} | {'Average Time (s)':<18} | {'Relative Speed'}")
    print("-" * 65)

    for name, func in methods.items():
        test_y = y_jax if "JAX" in name else y

        start_time = time.perf_counter()
        for _ in range(iterations):
            _ = func(test_y, dx)
        end_time = time.perf_counter()

        avg_time = (end_time - start_time) / iterations
        results[name] = avg_time

    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]))
    baseline_time = list(sorted_results.values())[0]

    for name, avg_time in sorted_results.items():
        relative = avg_time / baseline_time
        print(f"{name:<25} | {avg_time:.6f} s         | {relative:.2f}x")


if __name__ == "__main__":
    run_benchmark()
