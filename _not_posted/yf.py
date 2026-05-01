import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import yfinance as yf

    return (yf,)


@app.cell
def _():
    from urllib.parse import urlparse

    link = urlparse(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks"
    ).geturl()
    return (link,)


@app.cell
def _(link):
    from io import StringIO

    import pandas as pd
    import requests

    response = requests.get(
        link,
        headers={"User-Agent": "Mozilla/5.0 (compatible; dataset-updater/1.0)"},
        timeout=30,
    )
    response.raise_for_status()

    df = pd.read_html(StringIO(response.text), header=0)[0]
    tickers = df["Symbol"].to_list()
    return (tickers,)


@app.cell
def _(tickers, yf):
    yf_df = yf.download(
        tickers=tickers,
        start="2006-01-01",
        group_by="ticker",
    )
    return (yf_df,)


@app.cell
def _(yf_df):
    stacked = (
        yf_df.stack(level=[0])
        .reset_index()
        .rename(
            columns=lambda x: str(x).lower(),
        )
    )
    stacked.info()
    return (stacked,)


@app.cell
def _(stacked):
    from pathlib import Path

    import polars as pl
    import polars.selectors as cs

    ticker_path = Path("assets") / "data" / "ticker_data.arrow"

    df_pl = (
        pl.from_pandas(stacked)
        .with_columns(
            pl.col(pl.Float64).cast(pl.Float32).round(4),
            pl.col("date").cast(pl.Date),
        )
        .filter(
            ~pl.all_horizontal(cs.numeric().is_nan()),
        )
        .select(
            pl.all().exclude("adj close"),
        )
    )

    df_pl.estimated_size(unit="mb")
    return df_pl, ticker_path


@app.cell
def _(df_pl, ticker_path) -> None:
    df_pl.write_ipc(
        ticker_path,
        compression="zstd",
    )


if __name__ == "__main__":
    app.run()
