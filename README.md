# 📊 E-commerce Sales Analytics

[![Live Demo](https://img.shields.io/badge/▶_Live_Demo-Streamlit-ff4b4b.svg)](https://ecommerce-sales-analytics-wvxwhygjbuwjxelgsgeypy.streamlit.app)
[![CI](https://github.com/Tejaswini-Bollikonda/ecommerce-sales-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Tejaswini-Bollikonda/ecommerce-sales-analytics/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An **end-to-end data analysis project** — from raw, messy data to an interactive,
multi-tab dashboard — built with Python, pandas, and Streamlit. It analyses three
years of synthetic online-retail orders to answer real business questions: *Where
does our revenue come from? Is our discounting strategy actually profitable? Who
are our most valuable customers?*

> **🔗 [Try the live dashboard →](https://ecommerce-sales-analytics-wvxwhygjbuwjxelgsgeypy.streamlit.app)**
>
> Synthetic data is generated locally, so the whole project also runs anywhere with
> **no downloads or API keys**.

![Dashboard preview](assets/dashboard_preview.png)

---

## ✨ What this demonstrates

| Skill | Where to look |
|-------|---------------|
| Data cleaning & wrangling | [`src/data_prep.py`](src/data_prep.py) |
| Reusable analysis logic (KPIs, aggregations) | [`src/analysis.py`](src/analysis.py) |
| Exploratory data analysis & storytelling | [`notebooks/01_exploratory_analysis.ipynb`](notebooks/01_exploratory_analysis.ipynb) |
| Interactive, multi-tab dashboard | [`app.py`](app.py) |
| Considered data visualization (colorblind-safe palette, one visual system) | [`app.py`](app.py) |
| Unit tests + CI | [`tests/`](tests/) · [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Reproducible, well-structured code | project layout below |

---

## 📊 The dashboard

A filterable analytics workspace organised into four tabs:

| Tab | What it answers |
|-----|-----------------|
| **📈 Overview** | Headline KPIs with **year-over-year deltas**, sales & profit trend, category and regional breakdowns |
| **💰 Profitability** | Profit-margin-over-time, discount-vs-margin analysis, sales by ship mode, and an auto-generated insight |
| **📦 Products** | Top products by revenue and a **category-profitability** view (revenue vs. margin vs. profit) |
| **👥 Customers** | Top customers, segment mix, and revenue-concentration analysis |

Global filters (date range, region, category, segment) update every chart at once,
and the filtered dataset can be exported to CSV. Chart colors use a **colorblind-safe
categorical palette** validated for contrast and CVD separation, applied through one
shared visual system so every figure reads as part of the same product.

---

## 🚀 Quick start

```bash
# 1. Clone and enter the project
git clone https://github.com/Tejaswini-Bollikonda/ecommerce-sales-analytics.git
cd ecommerce-sales-analytics

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the sample dataset
python data/generate_data.py

# 5a. Explore in the notebook...
jupyter notebook notebooks/01_exploratory_analysis.ipynb

# 5b. ...or launch the interactive dashboard
streamlit run app.py
```

---

## 🗂️ Project structure

```
ecommerce-sales-analytics/
├── app.py                     # Multi-tab Streamlit dashboard
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Test/CI dependencies
├── .streamlit/config.toml     # Dashboard theme
├── data/
│   └── generate_data.py       # Creates realistic, intentionally-messy sample data
├── src/
│   ├── data_prep.py           # Load + clean pipeline
│   └── analysis.py            # KPIs and aggregations (shared by notebook & app)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb   # The EDA narrative
├── tests/                     # pytest suite for cleaning + analysis
└── .github/workflows/ci.yml   # Runs the tests on every push
```

The same functions in `src/` power **both** the notebook and the dashboard, so the
numbers never drift between your report and your app.

---

## 🔍 Key findings

- **Seasonality** — sales climb every Q4 with holiday demand.
- **Category mix** — Technology drives the most revenue; Office Supplies is
  high-volume but low-value.
- **Discounting erodes profit** — average margin drops sharply beyond ~20%
  discount, with the deepest band flirting with losses.
- **Customer concentration** — a small share of customers drives a large share of
  revenue, pointing to a clear retention opportunity.

---

## ✅ Tests

Unit tests cover the cleaning pipeline and every analysis function:

```bash
pip install -r requirements-dev.txt
pytest -q
```

They run automatically on every push via **GitHub Actions** (see the CI badge above).

## 🛠️ Built with

`pandas` · `numpy` · `matplotlib` / `seaborn` · `plotly` · `streamlit` · `pytest`

## 📄 License

MIT — feel free to fork and adapt. See [LICENSE](LICENSE).
