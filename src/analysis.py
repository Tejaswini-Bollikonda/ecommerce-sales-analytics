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


def sales_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
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


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Best-selling products by revenue, with profit and order count."""
    return (
        df.groupby("product")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(profit_margin=lambda d: (d["profit"] / d["sales"]).round(4))
        .sort_values("sales", ascending=False)
        .head(n)
        .reset_index()
    )


def sales_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Sales, profit, orders and margin grouped by customer segment."""
    return sales_by(df, "segment")


def margin_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """Monthly profit margin (profit / sales) — the profitability trend line."""
    grouped = (
        df.set_index("order_date")
        .resample(freq)
        .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    grouped["profit_margin"] = (grouped["profit"] / grouped["sales"]).round(4)
    return grouped


def yoy_deltas(df: pd.DataFrame) -> dict[str, float | tuple | None]:
    """Year-over-year growth (%) for headline metrics: latest full year vs prior.

    Returns an empty dict when the filtered data spans fewer than two years, so
    the dashboard can simply omit the delta arrows in that case.
    """
    years = sorted(df["order_year"].unique())
    if len(years) < 2:
        return {}
    cur, prev = years[-1], years[-2]
    c, p = df[df["order_year"] == cur], df[df["order_year"] == prev]

    def pct(now: float, before: float) -> float | None:
        return None if not before else round((now - before) / before * 100, 1)

    def aov(frame: pd.DataFrame) -> float:
        orders = frame["order_id"].nunique()
        return frame["sales"].sum() / orders if orders else 0.0

    return {
        "total_sales": pct(c["sales"].sum(), p["sales"].sum()),
        "total_profit": pct(c["profit"].sum(), p["profit"].sum()),
        "total_orders": pct(c["order_id"].nunique(), p["order_id"].nunique()),
        "avg_order_value": pct(aov(c), aov(p)),
        "avg_profit_margin": pct(
            c["profit"].sum() / c["sales"].sum(),
            p["profit"].sum() / p["sales"].sum(),
        ),
        "_years": (int(prev), int(cur)),
    }
