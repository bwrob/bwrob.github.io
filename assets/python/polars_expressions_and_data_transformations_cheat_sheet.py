"""Cheat sheet for Polars expressions in Finance.

This module demonstrates financial metrics and transformations using Polars,
including log returns, realized volatility, Sharpe ratio, and correlation.
"""

import pathlib

import polars as pl
import polars.selectors as cs


def main() -> None:
    """Run Polars finance demonstration examples."""
    # 0. Load Data
    data_path = pathlib.Path(__file__).parent.parent / "data" / "ticker_data.arrow"
    if not data_path.exists():
        print(f"Data not found at {data_path}.")
        return

    df = pl.read_ipc(data_path).sort(["ticker", "date"])

    # 1. Feature Engineering (Log Returns & Volatility)
    print("1. Feature Engineering:")
    df = df.with_columns(
        ret=(pl.col("close") / pl.col("close").shift(1)).log().over("ticker"),
    ).with_columns(
        vol=(pl.col("ret").rolling_std(window_size=21) * (252**0.5)).over("ticker")
    )
    print(df.select("date", "ticker", "ret", "vol").tail(3))

    # 2. Aggregations (Risk Metrics)
    print("\n2. Risk Aggregations:")
    risk = (
        df.group_by("ticker")
        .agg(
            ann_ret=pl.col("ret").mean() * 252,
            ann_vol=pl.col("ret").std() * (252**0.5),
            max_dd=(pl.col("close") / pl.col("close").cum_max() - 1).min(),
        )
        .with_columns(sharpe=pl.col("ann_ret") / pl.col("ann_vol"))
        .sort("sharpe", descending=True)
    )
    print(risk.head(5))

    # 3. Selectors & Shocks
    print("\n3. Selectors (1% Price Shock):")
    shock_expr = (cs.starts_with("open", "high", "low", "close") * 1.01).name.suffix(
        "_shock"
    )
    print(df.select("ticker", shock_expr).head(3))

    # 4. Window Functions (Cross-sectional Relative Strength)
    print("\n4. Window Functions (Relative Strength):")
    rel_strength = df.with_columns(
        rel_to_market=pl.col("close") / pl.col("close").mean().over("date")
    )
    print(rel_strength.select("date", "ticker", "rel_to_market").head(3))

    # 5. Correlation Matrix
    print("\n5. Correlation Matrix:")
    wide_ret = df.pivot(index="date", on="ticker", values="ret").drop_nulls()
    corr = wide_ret.select(cs.numeric()).corr()
    print(corr.head(5))


if __name__ == "__main__":
    main()
