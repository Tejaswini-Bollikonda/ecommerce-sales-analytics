"""Tests for the analysis functions in src/analysis.py."""

from __future__ import annotations

import pandas as pd

from src import analysis
from src.data_prep import clean


def test_kpis_are_consistent(raw_df):
    df = clean(raw_df)
    k = analysis.kpis(df)
    # Total sales equals the sum of the sales column.
    assert k["total_sales"] == df["sales"].sum()
    # Average order value = total sales / number of orders.
    assert k["avg_order_value"] == df["sales"].sum() / df["order_id"].nunique()
    assert k["unique_customers"] == df["customer_id"].nunique()


def test_sales_by_is_sorted_descending(raw_df):
    df = clean(raw_df)
    out = analysis.sales_by(df, "category")
    assert list(out["sales"]) == sorted(out["sales"], reverse=True)


def test_sales_by_top_n_limits_rows(raw_df):
    df = clean(raw_df)
    out = analysis.sales_by(df, "category", top=1)
    assert len(out) == 1


def test_sales_over_time_returns_expected_columns(raw_df):
    df = clean(raw_df)
    out = analysis.sales_over_time(df)
    assert {"order_date", "sales", "profit"}.issubset(out.columns)
    assert pd.api.types.is_datetime64_any_dtype(out["order_date"])


def test_top_customers_respects_n(raw_df):
    df = clean(raw_df)
    out = analysis.top_customers(df, n=1)
    assert len(out) == 1
    assert {"customer_id", "sales", "orders"}.issubset(out.columns)
