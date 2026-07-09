"""
Data cleaning and preparation.

Turns the raw, messy CSV from ``data/generate_data.py`` into a tidy, analysis-ready
DataFrame. Every transformation is small, named, and testable — the way you'd want
a reviewer on GitHub to read it.
"""

from __future__ import annotations

import os

import pandas as pd

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce_orders_raw.csv")


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    """Load the raw CSV, parsing dates. Raises a friendly error if it's missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find {path!r}. Run `python data/generate_data.py` first."
        )
    return pd.read_csv(path, parse_dates=["order_date"])


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the full cleaning pipeline and return a fresh, tidy DataFrame."""
    df = df.copy()

    # 1) Drop exact duplicate rows.
    df = df.drop_duplicates()

    # 2) Standardize categorical text: strip whitespace, title-case segments/regions.
    for col in ["segment", "region", "country", "category", "product", "ship_mode"]:
        df[col] = df[col].astype("string").str.strip()
    df["segment"] = df["segment"].str.title()
    df["region"] = df["region"].str.title()

    # 3) Fix invalid quantities (negative values were data-entry errors).
    df["quantity"] = df["quantity"].abs()

    # 4) Handle missing values.
    df["segment"] = df["segment"].fillna("Unknown")
    df["ship_mode"] = df["ship_mode"].fillna("Standard")
    # Profit is numeric — impute from a typical margin on that row's sales.
    typical_margin = (df["profit"] / df["sales"]).median()
    df["profit"] = df["profit"].fillna((df["sales"] * typical_margin).round(2))

    # 5) Derived columns useful for time-series and cohort analysis.
    df["order_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["order_year"] = df["order_date"].dt.year
    df["profit_margin"] = (df["profit"] / df["sales"]).round(4)

    return df.reset_index(drop=True)


def load_clean(path: str = RAW_PATH) -> pd.DataFrame:
    """Convenience: load the raw file and return it cleaned in one call."""
    return clean(load_raw(path))


if __name__ == "__main__":
    raw = load_raw()
    cleaned = clean(raw)
    print(f"Raw rows:     {len(raw):,}")
    print(f"Cleaned rows: {len(cleaned):,}")
    print("\nMissing values after cleaning:")
    print(cleaned.isna().sum())
