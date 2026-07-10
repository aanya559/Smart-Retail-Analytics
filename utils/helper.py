"""
utils/helper.py
Columns produced by generate_data.py:
  date, store_id, region, category, department, product,
  units_sold, unit_price, revenue, profit, promotion, holiday,
  discount, temperature, fuel_price, cpi, unemployment, forecast
"""
import calendar
import os

import numpy as np
import pandas as pd
import streamlit as st
import joblib


# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(path: str = "data/sales.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])

    # Derived time columns
    df["year"]         = df["date"].dt.year
    df["month"]        = df["date"].dt.month
    df["month_name"]   = df["date"].dt.strftime("%b")
    df["quarter"]      = df["date"].dt.quarter
    df["day_of_week"]  = df["date"].dt.dayofweek
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["month_year"]   = df["date"].dt.to_period("M").astype(str)

    # Ensure int flags
    df["promotion"] = df["promotion"].astype(int)
    df["holiday"]   = df["holiday"].astype(int)

    # store_id is already "Store 01" — use it directly as store_name
    df["store_name"] = df["store_id"].astype(str)

    # Derived metrics
    df["profit_margin"] = (df["profit"] / df["revenue"].clip(lower=0.01) * 100).round(2)

    # unit_price may already exist; compute if missing
    if "unit_price" not in df.columns:
        df["unit_price"] = (df["revenue"] / df["units_sold"].clip(lower=1)).round(2)

    # department is optional — create a placeholder if absent
    if "department" not in df.columns:
        df["department"] = df["category"]

    return df


# ─────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model(path: str = "model/forecast.pkl"):
    if not os.path.exists(path):
        return None
    return joblib.load(path)


# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:10px 0 6px 0'>"
            "<span style='font-size:2rem'>🛒</span><br>"
            "<span style='font-weight:700;font-size:1.1rem;color:#38bdf8'>Smart Retail</span><br>"
            "<span style='font-size:0.72rem;color:#94a3b8'>Analytics Dashboard</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("### 🔍 Filters")

        years = sorted(df["year"].unique())
        sel_years = st.multiselect("📅 Year", years, default=years)

        months = list(range(1, 13))
        sel_months = st.multiselect(
            "📅 Month", months, default=months,
            format_func=lambda x: calendar.month_abbr[x],
        )

        stores = sorted(df["store_name"].unique())
        sel_stores = st.multiselect("🏪 Store", stores, default=stores)

        regions = sorted(df["region"].unique())
        sel_regions = st.multiselect("🌍 Region", regions, default=regions)

        categories = sorted(df["category"].unique())
        sel_categories = st.multiselect("🛒 Category", categories, default=categories)

        departments = sorted(df["department"].unique())
        sel_departments = st.multiselect("🏬 Department", departments, default=departments)

        st.markdown("---")
        holiday_opt = st.selectbox("🎉 Holiday", ["All", "Holiday Only", "Non-Holiday"])
        promo_opt   = st.selectbox("🏷️ Promotion", ["All", "With Promotion", "No Promotion"])

    mask = (
        df["year"].isin(sel_years)
        & df["month"].isin(sel_months)
        & df["store_name"].isin(sel_stores)
        & df["region"].isin(sel_regions)
        & df["category"].isin(sel_categories)
        & df["department"].isin(sel_departments)
    )
    if holiday_opt == "Holiday Only":
        mask &= df["holiday"] == 1
    elif holiday_opt == "Non-Holiday":
        mask &= df["holiday"] == 0
    if promo_opt == "With Promotion":
        mask &= df["promotion"] == 1
    elif promo_opt == "No Promotion":
        mask &= df["promotion"] == 0

    return df[mask].copy()


# ─────────────────────────────────────────────
# KPI computation
# ─────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame) -> dict:
    total_revenue = df["revenue"].sum()
    total_profit  = df["profit"].sum()
    total_orders  = len(df)
    total_units   = df["units_sold"].sum()
    num_stores    = df["store_name"].nunique()
    avg_order_val = df["revenue"].mean() if total_orders > 0 else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    monthly = df.groupby("month_year")["revenue"].sum().sort_index()
    if len(monthly) >= 2:
        mom_growth = (monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100
    else:
        mom_growth = 0.0

    avg_temp = df["temperature"].mean() if "temperature" in df.columns else None
    avg_cpi  = df["cpi"].mean() if "cpi" in df.columns else None

    return {
        "total_revenue": total_revenue,
        "total_profit":  total_profit,
        "total_orders":  total_orders,
        "total_units":   total_units,
        "num_stores":    num_stores,
        "avg_order_val": avg_order_val,
        "profit_margin": profit_margin,
        "mom_growth":    mom_growth,
        "avg_temp":      avg_temp,
        "avg_cpi":       avg_cpi,
    }


# ─────────────────────────────────────────────
# AI Business Insights (rules-based)
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame) -> list:
    insights = []
    if df.empty:
        return [{"icon": "⚠️", "title": "No Data",
                 "body": "Apply filters to see data.", "type": "warning"}]

    # 1. Top revenue region
    region_rev = df.groupby("region")["revenue"].sum()
    top_region = region_rev.idxmax()
    top_pct    = region_rev.max() / region_rev.sum() * 100
    insights.append({
        "icon": "🌍", "title": f"{top_region} Region Leads Sales",
        "body": (f"{top_region} contributes {top_pct:.1f}% of total revenue — "
                 "the strongest performing region."),
        "type": "success",
    })

    # 2. Top category
    cat_rev     = df.groupby("category")["revenue"].sum()
    top_cat     = cat_rev.idxmax()
    top_cat_pct = cat_rev.max() / cat_rev.sum() * 100
    insights.append({
        "icon": "🏆", "title": f"{top_cat} is the Top Category",
        "body": f"{top_cat} accounts for {top_cat_pct:.1f}% of total revenue.",
        "type": "success",
    })

    # 3. Promotion impact
    promo_mean    = df[df["promotion"] == 1]["revenue"].mean() if df["promotion"].sum() > 0 else None
    no_promo_mean = df[df["promotion"] == 0]["revenue"].mean() if (df["promotion"] == 0).sum() > 0 else None
    if promo_mean and no_promo_mean and no_promo_mean > 0:
        lift = (promo_mean - no_promo_mean) / no_promo_mean * 100
        insights.append({
            "icon": "✅" if lift > 0 else "⚠️",
            "title": "Promotion Impact",
            "body": (f"Promotional days average ₹{promo_mean:,.0f} vs ₹{no_promo_mean:,.0f} on "
                     f"regular days — a {abs(lift):.1f}% {'lift' if lift > 0 else 'drop'}."),
            "type": "success" if lift > 0 else "warning",
        })

    # 4. Holiday effect
    hol_mean    = df[df["holiday"] == 1]["revenue"].mean() if df["holiday"].sum() > 0 else None
    no_hol_mean = df[df["holiday"] == 0]["revenue"].mean() if (df["holiday"] == 0).sum() > 0 else None
    if hol_mean and no_hol_mean and no_hol_mean > 0:
        multiplier = hol_mean / no_hol_mean
        insights.append({
            "icon": "🎉", "title": "Holiday Sales Multiplier",
            "body": (f"Holiday sales are {multiplier:.2f}x compared to regular days "
                     f"(₹{hol_mean:,.0f} vs ₹{no_hol_mean:,.0f} avg)."),
            "type": "info",
        })

    # 5. Lowest profit store
    store_p   = df.groupby("store_name")["profit"].sum()
    low_store = store_p.idxmin()
    low_val   = store_p.min()
    insights.append({
        "icon": "⚠️", "title": f"{low_store} Needs Attention",
        "body": (f"{low_store} has the lowest profit at ₹{low_val:,.0f}. "
                 "Consider reviewing pricing strategy and inventory."),
        "type": "warning",
    })

    # 6. Best sales month
    monthly_rev = df.groupby("month")["revenue"].sum()
    best_month  = monthly_rev.idxmax()
    insights.append({
        "icon": "📅", "title": "Peak Sales Month",
        "body": (f"{calendar.month_name[best_month]} records the highest revenue — "
                 "ideal window for promotions and stocking."),
        "type": "info",
    })

    # 7. Top department
    dept_rev  = df.groupby("department")["revenue"].sum()
    top_dept  = dept_rev.idxmax()
    top_d_pct = dept_rev.max() / dept_rev.sum() * 100
    insights.append({
        "icon": "🏬", "title": f"{top_dept} is the Top Department",
        "body": f"{top_dept} department generates {top_d_pct:.1f}% of revenue — a key growth driver.",
        "type": "success",
    })

    # 8. CPI context
    if "cpi" in df.columns:
        avg_cpi = df["cpi"].mean()
        insights.append({
            "icon": "📊", "title": "Economic Context",
            "body": (f"Average CPI across the selected period is {avg_cpi:.1f}, "
                     "indicating the macro price environment."),
            "type": "info",
        })

    # 9. YoY growth (if multi-year)
    if df["year"].nunique() > 1:
        yoy  = df.groupby("year")["revenue"].sum()
        yrs  = sorted(yoy.index)
        growth = (yoy[yrs[-1]] - yoy[yrs[-2]]) / yoy[yrs[-2]] * 100
        insights.append({
            "icon": "📈", "title": "YoY Revenue Growth",
            "body": (f"Revenue {'grew' if growth > 0 else 'fell'} {abs(growth):.1f}% "
                     f"from {yrs[-2]} to {yrs[-1]} "
                     f"(₹{yoy[yrs[-2]]/1e6:.2f}M → ₹{yoy[yrs[-1]]/1e6:.2f}M)."),
            "type": "success" if growth > 0 else "warning",
        })

    return insights


# ─────────────────────────────────────────────
# Aggregation helpers
# ─────────────────────────────────────────────
def monthly_agg(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("month_year")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            units=("units_sold", "sum"),
            orders=("revenue", "count"),
        )
        .reset_index()
        .sort_values("month_year")
    )


def rolling_avg(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def color_scale() -> list:
    return [
        "#38bdf8", "#818cf8", "#34d399", "#fb923c",
        "#f472b6", "#a78bfa", "#fbbf24", "#60a5fa",
    ]
