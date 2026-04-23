import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium", layout_file="layouts/button.grid.json")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """This is a markdown cell. It can contain **formatted** text,

        [links](https://marimo.dev), and more."""
    )
    return (mo,)


@app.cell
def _(mo):
    slider = mo.ui.slider(start=1, stop=42, full_width=True)
    slider
    return (slider,)


@app.cell
def _(slider):
    slider.value
    return


@app.cell
def _(slider):

    import numpy as np
    import polars as pl

    np.random.seed(slider.value)

    df = pl.DataFrame(
        {
            "nrs": [1, 2, 3, None, 5],
            "names": ["foo", "ham", "spam", "egg", "spam"],
            "random": np.random.rand(5),
            "groups": ["A", "A", "B", "A", "B"],
        }
    )
    df
    return


if __name__ == "__main__":
    app.run()
