"""Tests for the cleaning pipeline in src/data_prep.py."""

from __future__ import annotations

from src.data_prep import clean


def test_removes_duplicate_rows(raw_df):
    cleaned = clean(raw_df)
    # 4 raw rows, one is an exact duplicate -> 3 remain.
    assert len(cleaned) == 3


def test_no_missing_values_remain(raw_df):
    cleaned = clean(raw_df)
    assert cleaned.isna().sum().sum() == 0


def test_negative_quantity_is_fixed(raw_df):
    cleaned = clean(raw_df)
    assert (cleaned["quantity"] > 0).all()


def test_text_is_standardized(raw_df):
    cleaned = clean(raw_df)
    # " Asia " -> "Asia", "CORPORATE" -> "Corporate"
    assert "Asia" in cleaned["region"].values
    assert cleaned["region"].str.startswith(" ").sum() == 0
    assert "Corporate" in cleaned["segment"].values


def test_derived_columns_exist(raw_df):
    cleaned = clean(raw_df)
    for col in ("order_month", "order_year", "profit_margin"):
        assert col in cleaned.columns


def test_clean_does_not_mutate_input(raw_df):
    before = len(raw_df)
    _ = clean(raw_df)
    assert len(raw_df) == before  # original untouched
