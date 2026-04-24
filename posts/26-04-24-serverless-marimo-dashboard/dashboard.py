import marimo

__generated_with = "0.23.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    text = mo.md(
        """This is a markdown cell. It can contain **formatted** text, [links](https://marimo.dev), and more."""
    )
    return mo, text


@app.cell
def _(mo):
    img = mo.image(src="https://bwrob.github.io/assets/logo/python_mug.png", width=100)
    return (img,)


@app.cell
def _(mo):
    slider = mo.ui.slider(start=1, stop=42, full_width=True)
    return (slider,)


@app.cell
def _(slider):
    v = slider.value
    return (v,)


@app.cell
def _(slider):

    import numpy as np
    import polars as pl

    np.random.seed(slider.value)

    df = pl.DataFrame(
        {
            "nrs": [1, 2, 3, 4, 5],
            "names": ["foo", "ham", "spam", "egg", "spam"],
            "random": np.random.rand(5),
            "groups": ["A", "A", "B", None, "B"],
        }
    )
    return (df,)


@app.cell
def _(df, img, mo, slider, text, v):
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
