# Incubation Drawer (`_not_posted/`)

This directory serves as the local scratchpad, research drawer, and staging area for
unreleased technical blog posts, reproducible benchmarks, and prototype scripts.

> [!NOTE]
> This folder is intentionally excluded from Quarto site rendering, linter rules,
> formatting checks, and type checkers (`_quarto.yml`, `pyproject.toml`, `pyrefly.toml`).

---

## Directory Index

| Section | Topic | Key Contents | Target Blog Categories |
| :--- | :--- | :--- | :--- |
| **`mixins/`** | Multiple Inheritance & Mixin Patterns | 6-part draft series (`01-basics` through `06-dumbify`), `linear_inheritance.py`, `mixins.txt` | `Python Recipes` |
| **`quant-finance/`** | Quantitative Modeling & Market Data | QuantLib C++ shim prototype (`quant-lib-shim/`), interview prep (`interview-prep/`), SGH notes (`sgh-investment-banking/`), S&P 500 downloaders (`load_sp500_...py`, `yf_marimo_sp500.py`) | `Financial Markets`, `Career` |
| **`data-and-performance/`** | High-Performance Python & Numerical Computing | Polars batch accumulation (`polars-accumulation/`), Kahan/Numba floating-point sum (`float_sum.py`), Numba dynamic callables, NumPy gradient kernels, multithreaded pandas apply | `Data Science`, `Performance` |
| **`python-internals/`** | CPython Runtimes & Concurrency | CPython reference counting & immortal objects (`reference_count.md`), P-Core/E-Core dynamic CPU topology dashboard (`multiprocess_dashboard.py`), `.pth` startup injection (`pth_file_injection.py`), rich rotating logger, 2-arg `iter()` patterns | `Dev Env`, `Python Recipes`, `Performance` |
| **`pydantic-versioning/`** | Schema Evolution & Migrations | Pydantic model versioning patterns and compatibility layer tests | `Python Recipes`, `Data Science` |
| **`testing-patterns/`** | Test Doubles & Instrumentation | Proxies (`proxies/`) and Spies (`spies/`) design pattern drafts | `Python Recipes` |

---

## Promoting a Prototype into a Published Post

When a prototype or draft is ready to be developed into a full article, promote it using
the `create-post-stub` skill with `--from-not-posted`:

```bash
uv run python .agents/skills/create-post-stub/scripts/scaffold.py \
  --slug "cpython-immortal-objects" \
  --title "Understanding CPython Reference Counts and Immortal Objects" \
  --category "Performance" \
  --category "Python Recipes" \
  --description "Probing CPython reference counters, PEP 683, and sentinel values." \
  --from-not-posted "python-internals/reference_count.md"
```
