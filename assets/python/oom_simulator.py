"""A script to simulate Out of Memory (OOM) errors in pure Python and NumPy."""

import os
import resource
import secrets

import numpy as np


def limit_memory(max_bytes: int) -> None:
    """Set a virtual memory limit to trigger a Python MemoryError before OS SIGKILL."""
    resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))


def leak_python() -> None:
    """Trigger an OOM error by allocating progressively larger Python bytes objects."""
    print("Triggering OOM with a single pure Python bytes object...")
    current_size = 10 * 1024 * 1024  # Start at 10 MB
    data = None

    while True:
        if data is not None:
            del data  # Explicitly free memory before the next allocation

        print(f"Attempting to allocate {current_size // (1024**2)} MB bytes object...")
        data = os.urandom(current_size)
        current_size = int(current_size * 1.5)  # Grow by 50% each iteration


def leak_numpy() -> None:
    """Trigger an OOM error by allocating progressively larger NumPy float64 arrays."""
    print("Triggering OOM with a single native NumPy array...")
    current_elements = (10 * 1024 * 1024) // 8  # 8 bytes per float64
    arr = None

    while True:
        if arr is not None:
            del arr  # Explicitly free memory before the next allocation

        mb_size = (current_elements * 8) // (1024**2)
        print(f"Attempting to allocate {mb_size} MB float64 array...")

        # This single C-level malloc will eventually fail and raise MemoryError
        arr = np.ones(current_elements, dtype=np.float64)
        current_elements = int(current_elements * 1.5)  # Grow by 50% each iteration


if __name__ == "__main__":
    # Restrict the process to exactly 1 GB of memory
    limit_memory(1 * 1024**3)

    try:
        if secrets.choice([True, False]):
            leak_python()
        else:
            leak_numpy()
    except MemoryError:
        print(
            "\n[!] MemoryError caught. Memray can now flush the capture file to disk."
        )
