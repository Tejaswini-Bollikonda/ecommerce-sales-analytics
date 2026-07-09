"""
Analysis functions: KPIs and aggregations used by both the notebook and the app.

Keeping these here (instead of inline in the Streamlit app) means the exact same
numbers power the dashboard and any notebook / report — no drift between them.
"""

from __future__ import annotations

import pandas as pd


def kpis(df: pd.DataFrame) -> dict[str, float]:
    """Headline metrics for the top of a dashboard."""
    return {
        "total_sales": float(df["sales"].sum()),
        "total_profit": float(df["profit"].sum()),
        "avg_profit_margin": float(df["profit"].sum() / df["sales"].sum()),
        "total_orders": int(df["order_id"].nunique()),
        "unique_customers": int(df["customer_id"].nunique()),
        "avg_order_value": float(df["sales"].sum() / df["order_id"].nunique()),
    }


def sales_over_time(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Sales and profit aggregated by month (or any pandas offset alias)."""
    grouped = (
        df.set_index("order_date")
        .resample(freq)[["sales", "profit"]]
        .sum()
        .reset_index()
    )
    return grouped


def sales_by(df: pd.DataFrame, dimension: str, top: int | None = None) -> pd.DataFrame:
    """Sales, profit, orders and margin grouped by a categorical dimension."""
    out = (
        df.groupby(dimension)
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(profit_margin=lambda d: (d["profit"] / d["sales"]).round(4))
        .sort_values("sales", ascending=False)
        .reset_index()
    )
    return out.head(top) if top else out


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Highest-spending customers — the classic 'who matters most' question."""
    return (
        df.groupby("customer_id")
        .agg(sales=("sales", "sum"), orders=("order_id", "nunique"))
        .sort_values("sales", ascending=False)
        .head(n)
        .reset_index()
    )


def discount_vs_profit(df: pd.DataFrame) -> pd.DataFrame:
    """Does discounting actually help? Profit margin by discount band."""
    bands = pd.cut(
        df["discount"],
        bins=[-0.01, 0.0, 0.1, 0.2, 1.0],
        labels=["No discount", "1-10%", "11-20%", "21%+"],
    )
    return (
        df.groupby(bands, observed=True)
        .agg(
            avg_margin=("profit_margin", "mean"),
            total_profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
        .rename(columns={"discount": "discount_band"})
    )
