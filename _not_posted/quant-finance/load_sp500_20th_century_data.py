from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import polars as pl
import polars.selectors as cs
import requests
import yfinance as yf

if __name__ == "__main__":
    link = urlparse(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks"
    ).geturl()
    ticker_path = Path("assets") / "data" / "ticker_data.arrow"

    response = requests.get(
        link,
        headers={"User-Agent": "Mozilla/5.0 (compatible; dataset-updater/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    df = pd.read_html(StringIO(response.text), header=0)[0]
    tickers = df["Symbol"].to_list()

    yf_ticker_data = yf.download(
        tickers=tickers,
        start="2006-01-01",
        group_by="ticker",
    )

    stacked = (
        yf_ticker_data.stack(level=[0])
        .reset_index()
        .rename(columns=lambda x: str(x).lower())
    )

    df_pl = (
        pl.from_pandas(stacked)
        .with_columns(
            pl.col(pl.Float64).cast(pl.Float32).round(4),
            pl.col("date").cast(pl.Date),
        )
        .filter(~pl.all_horizontal(cs.numeric().is_nan()))
        .select(pl.all().exclude("adj close"))
    )
    df_pl.write_ipc(ticker_path, compression="zstd")
