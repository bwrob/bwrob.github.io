"""Example of a serverless Marimo dashboard.

This module demonstrates a simple interactive dashboard using the Marimo library,
featuring markdown, images, sliders, and data tables with Polars and NumPy.
"""

# ruff: noqa: ANN401 PLR0913
from __future__ import annotations

from typing import Any

import marimo
import marimo as mo
import marimo._runtime
import numpy as np
import polars as pl

__generated_with = "0.23.2"
app = marimo.App()


@app.cell
def _() -> tuple[marimo._runtime.packages.loader.LazyPackage, Any]:
    """Define the main title and markdown text."""
    text = mo.md(
        "This is a markdown cell. It can contain **formatted** text, "
        "[links](https://marimo.dev), and more."
    )
    return mo, text


@app.cell
def _(mo: Any) -> tuple[Any]:
    """Display the project logo."""
    img = mo.image(src="https://bwrob.github.io/assets/logo/python_mug.png", width=100)
    return (img,)


@app.cell
def _(mo: Any) -> tuple[Any]:
    """Create a slider for user interaction."""
    slider = mo.ui.slider(start=1, stop=42, full_width=True)
    return (slider,)


@app.cell
def _(slider: Any) -> tuple[Any]:
    """Capture the current value of the slider."""
    v = slider.value
    return (v,)


@app.cell
def _(slider: Any) -> tuple[pl.DataFrame]:
    """Generate a Polars DataFrame based on the slider value."""
    rng = np.random.default_rng(seed=slider.value)

    df = pl.DataFrame(
        {
            "nrs": [1, 2, 3, 4, 5],
            "names": ["foo", "ham", "spam", "egg", "spam"],
            "random": rng.random(5),
            "groups": ["A", "A", "B", None, "B"],
        }
    )
    return (df,)


@app.cell
def _(  # noqa: PLR0917
    df: pl.DataFrame, img: Any, mo: Any, slider: Any, text: Any, v: Any
) -> None:
    """Layout the dashboard components."""
    mo.vstack(
        [
            mo.hstack(
                [img, mo.vstack([text, slider, v])],
                widths=[1, 4],
                justify="space-around",
            ),
            df,
        ],
        gap=1,
    )


if __name__ == "__main__":
    app.run()
