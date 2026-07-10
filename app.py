"""
E-commerce Sales Analytics — executive dashboard (Streamlit + Plotly).

A multi-tab, filterable analytics workspace over 3 years of online-retail orders.
Chart colors use a colorblind-safe categorical palette validated against a light
surface; every figure shares one visual system (recessive grid, thin marks,
consistent ink).

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analysis import (
    discount_vs_profit,
    kpis,
    margin_over_time,
    sales_by,
    sales_by_segment,
    sales_over_time,
    top_customers,
    top_products,
    yoy_deltas,
)
from src.data_prep import load_clean

# --------------------------------------------------------------------------- #
# Design system — validated categorical palette + ink/grid tokens (light mode)
# --------------------------------------------------------------------------- #
PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]
INK, SECONDARY, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#ffffff"
GOOD, CRITICAL = "#0ca30c", "#d03b3b"
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# A little CSS to lift the default Streamlit look to dashboard-grade
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 2rem; padding-bottom: 2rem; max-width: 1300px; }}
      [data-testid="stMetric"] {{
        background: {SURFACE};
        border: 1px solid rgba(11,11,11,0.08);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px rgba(11,11,11,0.04);
      }}
      [data-testid="stMetricLabel"] p {{ color: {SECONDARY}; font-weight: 600; font-size: 0.82rem; }}
      [data-testid="stMetricValue"] {{ color: {INK}; font-weight: 700; }}
      .dash-title {{ font-size: 1.9rem; font-weight: 800; color: {INK}; margin-bottom: 0.1rem; }}
      .dash-sub {{ color: {SECONDARY}; font-size: 0.98rem; margin-top: 0; }}
      .insight {{
        background: #f0f6ff; border-left: 4px solid {PALETTE[0]};
        padding: 12px 16px; border-radius: 8px; color: {INK}; font-size: 0.92rem;
      }}
      hr {{ margin: 0.8rem 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@st.cache_data
def get_data() -> pd.DataFrame:
    return load_clean()


def money(x: float) -> str:
    if abs(x) >= 1e6:
        return f"${x / 1e6:.2f}M"
    if abs(x) >= 1e3:
        return f"${x / 1e3:.1f}K"
    return f"${x:,.0f}"


def delta_str(pct: float | None) -> str | None:
    return None if pct is None else f"{pct:+.1f}% YoY"


def style(fig: go.Figure, height: int = 360, legend: bool = True) -> go.Figure:
    """Apply the shared visual system to any Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=8, t=44, b=8),
        font=dict(family=FONT, color=INK, size=13),
        title=dict(font=dict(size=15, color=INK), x=0, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        hoverlabel=dict(font_size=12, font_family=FONT),
        colorway=PALETTE,
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS, tickfont=dict(color=MUTED), title_font=dict(color=SECONDARY))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED), title_font=dict(color=SECONDARY))
    if not legend:
        fig.update_layout(showlegend=False)
    return fig


# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
try:
    df = get_data()
except FileNotFoundError:
    st.error("No data found. Run `python data/generate_data.py` first, then reload.")
    st.stop()

# --------------------------------------------------------------------------- #
# Sidebar — filters
# --------------------------------------------------------------------------- #
st.sidebar.header("⚙️ Filters")

min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_d, max_d

regions = sorted(df["region"].dropna().unique())
region_sel = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(df["category"].dropna().unique())
cat_sel = st.sidebar.multiselect("Category", categories, default=categories)

segments = sorted(df["segment"].dropna().unique())
seg_sel = st.sidebar.multiselect("Segment", segments, default=segments)

mask = (
    (df["order_date"].dt.date >= start_d)
    & (df["order_date"].dt.date <= end_d)
    & df["region"].isin(region_sel)
    & df["category"].isin(cat_sel)
    & df["segment"].isin(seg_sel)
)
fdf = df[mask]

st.sidebar.markdown("---")
if not fdf.empty:
    st.sidebar.download_button(
        "⬇️ Download filtered data (CSV)",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="ecommerce_filtered.csv",
        mime="text/csv",
        width="stretch",
    )
st.sidebar.caption(f"Showing **{len(fdf):,}** of {len(df):,} orders")

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.markdown('<div class="dash-title">📊 E-commerce Sales Analytics</div>', unsafe_allow_html=True)
st.markdown(
    f'<p class="dash-sub">Performance across {start_d:%b %Y} – {end_d:%b %Y} · '
    f'{len(region_sel)} regions · {len(cat_sel)} categories</p>',
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("No orders match the current filters. Widen your selection in the sidebar.")
    st.stop()

# --------------------------------------------------------------------------- #
# KPI row (with year-over-year deltas where available)
# --------------------------------------------------------------------------- #
k = kpis(fdf)
d = yoy_deltas(fdf)
st.markdown("")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", money(k["total_sales"]), delta_str(d.get("total_sales")))
c2.metric("Total Profit", money(k["total_profit"]), delta_str(d.get("total_profit")))
c3.metric("Profit Margin", f"{k['avg_profit_margin']:.1%}", delta_str(d.get("avg_profit_margin")))
c4.metric("Orders", f"{k['total_orders']:,}", delta_str(d.get("total_orders")))
c5.metric("Avg Order Value", money(k["avg_order_value"]), delta_str(d.get("avg_order_value")))
if d.get("_years"):
    st.caption(f"↑↓ deltas compare **{d['_years'][1]}** vs **{d['_years'][0]}** (year over year).")

st.markdown("---")

# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
tab_overview, tab_profit, tab_products, tab_customers = st.tabs(
    ["📈 Overview", "💰 Profitability", "📦 Products", "👥 Customers"]
)

# ------------------------------- Overview ---------------------------------- #
with tab_overview:
    trend = sales_over_time(fdf, freq="ME")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["order_date"], y=trend["sales"], name="Sales",
                             mode="lines", line=dict(color=PALETTE[0], width=2)))
    fig.add_trace(go.Scatter(x=trend["order_date"], y=trend["profit"], name="Profit",
                             mode="lines", line=dict(color=PALETTE[1], width=2)))
    fig.update_layout(title="Sales & profit over time", hovermode="x unified")
    fig.update_yaxes(tickprefix="$", tickformat="~s")
    st.plotly_chart(style(fig), width="stretch")

    left, right = st.columns(2)
    with left:
        by_cat = sales_by(fdf, "category")
        fig = px.bar(by_cat.sort_values("sales"), x="sales", y="category", orientation="h",
                     title="Sales by category")
        fig.update_traces(marker_color=PALETTE[0], marker_line_width=0)
        fig.update_xaxes(tickprefix="$", tickformat="~s")
        st.plotly_chart(style(fig, height=320, legend=False), width="stretch")
    with right:
        by_region = sales_by(fdf, "region")
        fig = px.pie(by_region, names="region", values="sales", hole=0.55, title="Sales share by region")
        fig.update_traces(marker=dict(colors=PALETTE, line=dict(color=SURFACE, width=2)),
                          textposition="outside", textinfo="percent+label")
        st.plotly_chart(style(fig, height=320), width="stretch")

# ----------------------------- Profitability ------------------------------- #
with tab_profit:
    mot = margin_over_time(fdf, freq="ME")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mot["order_date"], y=mot["profit_margin"], name="Profit margin",
                             mode="lines", line=dict(color=PALETTE[0], width=2), fill="tozeroy",
                             fillcolor="rgba(42,120,214,0.08)"))
    fig.update_layout(title="Profit margin over time")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(style(fig, legend=False), width="stretch")

    left, right = st.columns(2)
    with left:
        disc = discount_vs_profit(fdf)
        fig = px.bar(disc, x="discount_band", y="avg_margin", title="Avg profit margin by discount band")
        # Sequential blue: deeper discount → lighter/receding, magnitude reads off length + hue.
        fig.update_traces(marker_color=SEQ_BLUE[4], marker_line_width=0)
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(style(fig, height=320, legend=False), width="stretch")
    with right:
        by_ship = sales_by(fdf, "ship_mode")
        fig = px.bar(by_ship.sort_values("sales"), x="sales", y="ship_mode", orientation="h",
                     title="Sales by ship mode")
        fig.update_traces(marker_color=PALETTE[1], marker_line_width=0)
        fig.update_xaxes(tickprefix="$", tickformat="~s")
        st.plotly_chart(style(fig, height=320, legend=False), width="stretch")

    worst = disc.loc[disc["avg_margin"].idxmin()]
    best = disc.loc[disc["avg_margin"].idxmax()]
    st.markdown(
        f'<div class="insight"><b>Insight:</b> orders with <b>{worst["discount_band"]}</b> '
        f'discounts average a <b>{worst["avg_margin"]:.1%}</b> margin versus '
        f'<b>{best["avg_margin"]:.1%}</b> at <b>{best["discount_band"]}</b> — deep discounts '
        f'drive revenue but erode profitability. Cap routine discounts and reserve deeper cuts '
        f'for clearance.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------- Products ---------------------------------- #
with tab_products:
    left, right = st.columns([3, 2])
    with left:
        prods = top_products(fdf, 10)
        fig = px.bar(prods.sort_values("sales"), x="sales", y="product", orientation="h",
                     title="Top 10 products by revenue")
        fig.update_traces(marker_color=PALETTE[0], marker_line_width=0)
        fig.update_xaxes(tickprefix="$", tickformat="~s")
        st.plotly_chart(style(fig, height=420, legend=False), width="stretch")
    with right:
        cat = sales_by(fdf, "category")
        fig = px.scatter(cat, x="sales", y="profit_margin", size="profit", color="category",
                         title="Category profitability", size_max=55)
        fig.update_traces(marker=dict(line=dict(color=SURFACE, width=2)))
        fig.update_xaxes(tickprefix="$", tickformat="~s")
        fig.update_yaxes(tickformat=".0%", title="Profit margin")
        st.plotly_chart(style(fig, height=420), width="stretch")

    st.dataframe(
        prods.style.format({"sales": "${:,.0f}", "profit": "${:,.0f}", "profit_margin": "{:.1%}"}),
        width="stretch", hide_index=True,
    )

# ------------------------------- Customers --------------------------------- #
with tab_customers:
    left, right = st.columns([3, 2])
    with left:
        tc = top_customers(fdf, 10)
        fig = px.bar(tc.sort_values("sales"), x="sales", y="customer_id", orientation="h",
                     title="Top 10 customers by revenue")
        fig.update_traces(marker_color=PALETTE[4], marker_line_width=0)
        fig.update_xaxes(tickprefix="$", tickformat="~s")
        st.plotly_chart(style(fig, height=420, legend=False), width="stretch")
    with right:
        seg = sales_by_segment(fdf)
        fig = px.pie(seg, names="segment", values="sales", hole=0.55, title="Sales by customer segment")
        fig.update_traces(marker=dict(colors=PALETTE, line=dict(color=SURFACE, width=2)),
                          textposition="outside", textinfo="percent+label")
        st.plotly_chart(style(fig, height=420), width="stretch")

    top_share = tc["sales"].sum() / fdf["sales"].sum()
    st.markdown(
        f'<div class="insight"><b>Insight:</b> the top 10 customers account for '
        f'<b>{top_share:.1%}</b> of revenue in the current selection — a concentrated base '
        f'that rewards retention and account-management focus.</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "Built with pandas · Streamlit · Plotly  |  Colorblind-safe palette  |  "
    "Synthetic data — see the project README for methodology."
)
