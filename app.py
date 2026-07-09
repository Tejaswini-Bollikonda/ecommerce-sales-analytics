"""
E-commerce Sales Analytics — interactive Streamlit dashboard.

Run:
    streamlit run app.py
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import (
    discount_vs_profit,
    kpis,
    sales_by,
    sales_over_time,
    top_customers,
)
from src.data_prep import load_clean

st.set_page_config(page_title="E-commerce Sales Analytics", page_icon="📊", layout="wide")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_clean()


def money(x: float) -> str:
    return f"${x:,.0f}"


# --------------------------------------------------------------------------- #
# Load data (with a friendly nudge if it hasn't been generated yet)
# --------------------------------------------------------------------------- #
try:
    df = get_data()
except FileNotFoundError:
    st.error("No data found. Run `python data/generate_data.py` first, then reload.")
    st.stop()

st.title("📊 E-commerce Sales Analytics")
st.caption("End-to-end exploratory analysis of 3 years of synthetic online-retail orders.")

# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.header("Filters")

years = sorted(df["order_year"].unique())
year_sel = st.sidebar.multiselect("Year", years, default=years)

regions = sorted(df["region"].dropna().unique())
region_sel = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(df["category"].dropna().unique())
cat_sel = st.sidebar.multiselect("Category", categories, default=categories)

mask = (
    df["order_year"].isin(year_sel)
    & df["region"].isin(region_sel)
    & df["category"].isin(cat_sel)
)
fdf = df[mask]

if fdf.empty:
    st.warning("No orders match the current filters. Widen your selection.")
    st.stop()

# --------------------------------------------------------------------------- #
# KPI row
# --------------------------------------------------------------------------- #
k = kpis(fdf)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", money(k["total_sales"]))
c2.metric("Total Profit", money(k["total_profit"]))
c3.metric("Avg Profit Margin", f"{k['avg_profit_margin']:.1%}")
c4.metric("Avg Order Value", money(k["avg_order_value"]))

c5, c6 = st.columns(2)
c5.metric("Orders", f"{k['total_orders']:,}")
c6.metric("Unique Customers", f"{k['unique_customers']:,}")

st.divider()

# --------------------------------------------------------------------------- #
# Trend over time
# --------------------------------------------------------------------------- #
st.subheader("Sales & profit over time")
trend = sales_over_time(fdf, freq="M")
fig = px.line(
    trend,
    x="order_date",
    y=["sales", "profit"],
    labels={"value": "Amount ($)", "order_date": "Month", "variable": "Metric"},
    markers=True,
)
fig.update_layout(legend_title_text="", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------- #
# Breakdown by dimension
# --------------------------------------------------------------------------- #
left, right = st.columns(2)

with left:
    st.subheader("Sales by category")
    by_cat = sales_by(fdf, "category")
    fig = px.bar(by_cat, x="category", y="sales", color="category", text_auto=".2s")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Sales by region")
    by_region = sales_by(fdf, "region")
    fig = px.pie(by_region, names="region", values="sales", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------- #
# Discount analysis — a real insight, not just a chart
# --------------------------------------------------------------------------- #
st.subheader("Does discounting pay off?")
disc = discount_vs_profit(fdf)
fig = px.bar(
    disc,
    x="discount_band",
    y="avg_margin",
    color="avg_margin",
    color_continuous_scale="RdYlGn",
    labels={"avg_margin": "Avg profit margin", "discount_band": "Discount band"},
)
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(fig, use_container_width=True)
st.info(
    "**Insight:** average profit margin falls sharply as discounts deepen — orders "
    "discounted 21%+ tend toward break-even or a loss. Deep discounts drive revenue "
    "but erode profitability."
)

# --------------------------------------------------------------------------- #
# Top customers
# --------------------------------------------------------------------------- #
st.subheader("Top 10 customers by sales")
st.dataframe(
    top_customers(fdf, 10).style.format({"sales": "${:,.0f}"}),
    use_container_width=True,
    hide_index=True,
)

st.caption("Built with pandas + Streamlit + Plotly · synthetic data · see README for details.")
