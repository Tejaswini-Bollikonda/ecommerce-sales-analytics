"""Shared pytest fixtures.

We build a tiny, hand-made DataFrame that mirrors the real schema — including the
same kinds of dirtiness (duplicates, mixed casing, a negative quantity, a missing
value) — so tests are fast and deterministic without needing the generated CSV.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def raw_df() -> pd.DataFrame:
    rows = [
        # order_id, date, cust, segment, region, country, category, product, qty, price, disc, sales, profit, ship
        ("ORD-1", "2023-01-15", "C-1", "Consumer", "Europe", "Germany", "Technology", "Laptop", 2, 500.0, 0.0, 1000.0, 300.0, "Standard"),
        ("ORD-2", "2023-02-20", "C-2", "CORPORATE", " Asia ", "India", "Furniture", "Desk", -3, 200.0, 0.2, 480.0, 50.0, "Express"),
        ("ORD-3", "2023-11-10", "C-1", "Home Office", "Europe", "France", "Office Supplies", "Pens", 5, 10.0, 0.0, 50.0, None, "Standard"),
        # exact duplicate of ORD-1 (should be dropped)
        ("ORD-1", "2023-01-15", "C-1", "Consumer", "Europe", "Germany", "Technology", "Laptop", 2, 500.0, 0.0, 1000.0, 300.0, "Standard"),
    ]
    cols = [
        "order_id", "order_date", "customer_id", "segment", "region", "country",
        "category", "product", "quantity", "unit_price", "discount", "sales",
        "profit", "ship_mode",
    ]
    df = pd.DataFrame(rows, columns=cols)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df
