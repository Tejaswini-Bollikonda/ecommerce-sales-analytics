"""
Generate a realistic, synthetic e-commerce orders dataset.

The data is intentionally *messy* (missing values, duplicate rows, inconsistent
casing, a few negative quantities) so that the cleaning step in the analysis has
something real to do — mirroring what you'd meet on the job.

Run:
    python data/generate_data.py
Produces:
    data/ecommerce_orders_raw.csv
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)  # reproducible
N_ORDERS = 10_000
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

REGIONS = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["United Kingdom", "Germany", "France", "Spain"],
    "Asia": ["India", "Japan", "Singapore"],
    "Oceania": ["Australia", "New Zealand"],
}

CATEGORIES = {
    "Technology": ["Laptop", "Smartphone", "Headphones", "Monitor", "Keyboard"],
    "Furniture": ["Office Chair", "Desk", "Bookcase", "Sofa", "Lamp"],
    "Office Supplies": ["Notebook", "Pens (Pack)", "Stapler", "Paper (Ream)", "Binder"],
}

# Rough average price per category to make revenue realistic.
CATEGORY_PRICE = {"Technology": 450, "Furniture": 220, "Office Supplies": 12}

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard", "Express", "Same Day", "Economy"]


def _random_dates(n: int) -> pd.Series:
    start = pd.Timestamp(START_DATE).value // 10**9
    end = pd.Timestamp(END_DATE).value // 10**9
    secs = RNG.integers(start, end, size=n)
    dates = pd.to_datetime(secs, unit="s")
    # Add mild seasonality: bump Nov/Dec (holiday) by resampling some rows into Q4.
    boost = RNG.random(n) < 0.15
    dates = dates.where(~boost, dates + pd.to_timedelta(RNG.integers(0, 60, n), unit="D"))
    # Keep everything inside the intended window — the seasonal shift can otherwise
    # spill a few orders past END_DATE into a near-empty trailing year.
    end_ts = pd.Timestamp(END_DATE)
    dates = dates.where(dates <= end_ts, end_ts)
    return dates


def generate() -> pd.DataFrame:
    regions = RNG.choice(list(REGIONS), size=N_ORDERS, p=[0.4, 0.3, 0.2, 0.1])
    countries = [RNG.choice(REGIONS[r]) for r in regions]

    categories = RNG.choice(list(CATEGORIES), size=N_ORDERS, p=[0.35, 0.25, 0.40])
    products = [RNG.choice(CATEGORIES[c]) for c in categories]

    base_price = np.array([CATEGORY_PRICE[c] for c in categories])
    unit_price = np.round(base_price * RNG.lognormal(mean=0.0, sigma=0.35, size=N_ORDERS), 2)

    quantity = RNG.integers(1, 12, size=N_ORDERS)
    discount = RNG.choice([0, 0.1, 0.15, 0.2, 0.3], size=N_ORDERS, p=[0.5, 0.2, 0.15, 0.1, 0.05])

    sales = np.round(unit_price * quantity * (1 - discount), 2)
    # Profit margin shrinks as discount grows; some orders lose money.
    margin = 0.35 - discount + RNG.normal(0, 0.05, N_ORDERS)
    profit = np.round(sales * margin, 2)

    df = pd.DataFrame(
        {
            "order_id": [f"ORD-{100000 + i}" for i in range(N_ORDERS)],
            "order_date": _random_dates(N_ORDERS),
            "customer_id": [f"CUST-{RNG.integers(1000, 3000)}" for _ in range(N_ORDERS)],
            "segment": RNG.choice(SEGMENTS, size=N_ORDERS, p=[0.5, 0.3, 0.2]),
            "region": regions,
            "country": countries,
            "category": categories,
            "product": products,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "sales": sales,
            "profit": profit,
            "ship_mode": RNG.choice(SHIP_MODES, size=N_ORDERS, p=[0.5, 0.25, 0.1, 0.15]),
        }
    )

    df = _add_realistic_mess(df)
    return df


def _add_realistic_mess(df: pd.DataFrame) -> pd.DataFrame:
    """Inject the kind of dirtiness real datasets have."""
    df = df.copy()

    # 1) Missing values scattered through a few columns.
    for col, frac in [("segment", 0.03), ("ship_mode", 0.02), ("profit", 0.01)]:
        idx = df.sample(frac=frac, random_state=1).index
        df.loc[idx, col] = np.nan

    # 2) Inconsistent casing / whitespace in categorical text.
    mixed = df.sample(frac=0.05, random_state=2).index
    df.loc[mixed, "segment"] = df.loc[mixed, "segment"].str.upper()
    df.loc[mixed, "region"] = " " + df.loc[mixed, "region"] + " "

    # 3) A handful of duplicate rows.
    dupes = df.sample(50, random_state=3)
    df = pd.concat([df, dupes], ignore_index=True)

    # 4) A few invalid negative quantities (data-entry errors).
    bad = df.sample(20, random_state=4).index
    df.loc[bad, "quantity"] = -df.loc[bad, "quantity"]

    return df.sample(frac=1, random_state=5).reset_index(drop=True)  # shuffle


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "ecommerce_orders_raw.csv")
    df = generate()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}")
    print(df.head())


if __name__ == "__main__":
    main()
