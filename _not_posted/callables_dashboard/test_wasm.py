import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium", sql_output="native")


@app.cell
def _():
    import marimo as mo
    import QuantLib as ql
    mo.md("Welcome")

    return mo, ql


@app.cell
def _(mo, ql):
    mo.md(ql.__version__)
    return


if __name__ == "__main__":
    app.run()
