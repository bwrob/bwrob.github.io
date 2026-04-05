import os

import polars as pl
import polars.selectors as cs
import seaborn as sns


def main() -> None:
    # 1. Setup & Expressions
    print("1. Setup & Expressions (Normalization chain):")
    df = pl.from_pandas(sns.load_dataset("iris"))
    norm_expr = (
        ((cs.numeric() - cs.numeric().mean()) / cs.numeric().std())
        .clip(-1, 1)
        .cast(pl.Float32)
        .name.suffix("_norm")
    )
    print(df.select(norm_expr).head(3))

    # 2. Transformations (Horizontal + Boolean + Coalesce)
    print("\n2. Transformations (Complex columns):")
    print(
        df.with_columns(
            max_dim=pl.max_horizontal(cs.numeric()),
            size_tag=pl.when(pl.col("sepal_length") > 6)
            .then(pl.lit("XL"))
            .otherwise(pl.lit("L")),
            combined=pl.coalesce(pl.col("sepal_length"), pl.col("sepal_width")),
        ).head(3)
    )

    # 3. Group Logic (Agg + Window + Rank)
    print("\n3. Group Logic (Aggregated Top-3 Mean + Rank):")
    print(
        df.group_by("species")
        .agg(
            n=pl.len(),
            avg_sepal=pl.col("sepal_length").mean(),
            top_3_sepal_avg=pl.col("sepal_length").sort(descending=True).head(3).mean(),
        )
        .with_columns(rank=pl.col("avg_sepal").rank("dense", descending=True))
    )

    # 4. Table Ops (Joins & Sets)
    print("\n4. Table Operations (Semi-join):")
    filter_df = pl.DataFrame({"species": ["setosa"]})
    print(df.join(filter_df, on="species", how="semi").head(3))

    # 5. Advanced Types (Time-series & List Eval)
    print("\n5. Advanced Types (List eval):")
    print(
        df.group_by("species")
        .agg(pl.col("petal_length").implode())
        .select(
            "species",
            top_2=pl.col("petal_length").list.eval(
                pl.element().sort(descending=True).head(2)
            ),
        )
    )

    # 6. Performance (Streaming)
    print("\n6. Performance (Streaming Scan->Transform->Sink):")
    df.write_csv("iris_temp.csv")
    (
        pl.scan_csv("iris_temp.csv")
        .filter(pl.col("sepal_length") > 5.0)
        .sink_csv("iris_final.csv")
    )
    print("Streaming complete. Cleaning up...")
    if os.path.exists("iris_temp.csv"):
        os.remove("iris_temp.csv")
    if os.path.exists("iris_final.csv"):
        os.remove("iris_final.csv")


if __name__ == "__main__":
    main()
