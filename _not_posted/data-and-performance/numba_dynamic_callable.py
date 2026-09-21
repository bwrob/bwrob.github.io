from numba import njit


# ==========================================
# 1. THE OUTER FUNCTION
# ==========================================
# This function accepts a callable. Numba uses "lazy compilation"
# to figure out the types when it's first called.
@njit
def apply_math_operation(func, x, y):
    return func(x, y)


# ==========================================
# 2. METHOD A: PRE-COMPILED CALLABLE
# ==========================================
# This function is compiled immediately when the script loads.
@njit
def add_precompiled(a, b):
    return a + b


# ==========================================
# 3. METHOD B: RUNTIME COMPILATION
# ==========================================
# This is just a normal, uncompiled Python function.
def multiply_dynamic(a, b):
    return a * b


def main() -> None:
    x, y = 5, 3

    # --- Executing Method A ---
    # Passing the pre-compiled function directly
    result_add = apply_math_operation(add_precompiled, x, y)
    print(f"Pre-compiled @njit function (Add):      {x} + {y} = {result_add}")

    # --- Executing Method B ---
    # Compile the normal Python function dynamically at runtime.
    # NOTE: This compilation step must happen in standard Python space,
    # and you should only do it once to avoid compilation overhead!
    compiled_multiply = njit(multiply_dynamic)

    # Now pass the newly compiled function into the outer Numba function
    result_mult = apply_math_operation(compiled_multiply, x, y)
    print(f"Runtime compiled njit function (Multi): {x} * {y} = {result_mult}")


if __name__ == "__main__":
    main()
