"""
pages/2_Forecasting.py — Updated for real dataset schema (no synthetic 'forecast' column)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import load_data, apply_sidebar_filters, compute_kpis, monthly_agg, load_model
from utils.charts import forecast_chart, rolling_avg_chart, monthly_growth_chart

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#080f1a;color:#f1f5f9;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1424,#111c30) !important;border-right:1px solid #1e2d45;}
[data-testid="stSidebar"] *{color:#cbd5e1 !important;} [data-testid="stSidebar"] h3{color:#38bdf8 !important;}
#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #1e3a5f;border-radius:14px;padding:18px 16px !important;box-shadow:0 4px 20px rgba(0,0,0,0.5);transition:transform 0.2s,box-shadow 0.2s;}
[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(56,189,248,0.15);}
[data-testid="stMetricLabel"]{color:#94a3b8 !important;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.06em;}
[data-testid="stMetricValue"]{color:#f8fafc !important;font-size:1.5rem;font-weight:700;}
h1{color:#38bdf8 !important;font-weight:700 !important;} h2{color:#e2e8f0 !important;} h3{color:#cbd5e1 !important;}
.stPlotlyChart{background:#0f172a;border-radius:14px;border:1px solid #1e2d45;padding:4px;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:#0f172a;border-radius:8px;padding:4px;}
[data-testid="stTabs"] [data-baseweb="tab"]{color:#94a3b8 !important;border-radius:6px;}
[data-testid="stTabs"] [aria-selected="true"]{background:#1e3a5f !important;color:#38bdf8 !important;}
::-webkit-scrollbar{width:6px;} ::-webkit-scrollbar-track{background:#0f172a;}
::-webkit-scrollbar-thumb{background:#334155;border-radius:4px;}
hr{border-color:#1e2d45;}
.stButton>button{background:linear-gradient(135deg,#0ea5e9,#6366f1);color:white !important;border:none;border-radius:8px;font-weight:600;padding:0.5rem 1.2rem;transition:opacity 0.2s,transform 0.2s;}
.stButton>button:hover{opacity:0.88;transform:translateY(-1px);}
</style>
"""

st.set_page_config(page_title="Forecasting — Smart Retail", page_icon="📅", layout="wide")
st.markdown(_CSS, unsafe_allow_html=True)

if st.session_state.get("df") is None:
    if os.path.exists("data/sales.csv"):
        st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.error("❌ data/sales.csv not found.")
        st.stop()

df_full = st.session_state["df"]
df = apply_sidebar_filters(df_full)

st.markdown("# 📅 Sales Forecasting")
st.markdown("<p style='color:#64748b;margin-top:-12px'>Historical trends · Rolling averages · YoY comparison · ML predictions</p>",
            unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

kpis = compute_kpis(df)
agg  = monthly_agg(df)

# ─── KPI Row ──────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue",   f"₹{kpis['total_revenue']/1e6:.2f}M")
c2.metric("📈 Total Profit",    f"₹{kpis['total_profit']/1e6:.2f}M",
          f"{kpis['profit_margin']:.1f}% margin")
c3.metric("📅 MoM Growth",      f"{kpis['mom_growth']:+.1f}%",
          delta_color="normal" if kpis["mom_growth"] >= 0 else "inverse")
c4.metric("📦 Total Units",     f"{kpis['total_units']:,}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Revenue Trend",
    "📉 Rolling Averages",
    "📅 Monthly Table",
    "📊 YoY Comparison",
])

with tab1:
    st.plotly_chart(forecast_chart(df), use_container_width=True)

    # Category comparison line chart
    st.markdown("#### 📊 Revenue Trend by Category")
    cat_monthly = (
        df.groupby(["month_year","category"])["revenue"]
        .sum().reset_index()
        .sort_values("month_year")
    )
    fig_cat = px.line(
        cat_monthly, x="month_year", y="revenue", color="category",
        color_discrete_sequence=["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6"],
        template="plotly_dark", markers=True,
        title="Monthly Revenue by Category",
        labels={"month_year":"Month","revenue":"Revenue (₹)","category":"Category"},
    )
    fig_cat.update_layout(height=380, margin=dict(l=10,r=10,t=60,b=10))
    st.plotly_chart(fig_cat, use_container_width=True)

with tab2:
    st.plotly_chart(rolling_avg_chart(df), use_container_width=True)
    st.markdown("""
    <div style="background:#1e293b;border-radius:10px;padding:14px 18px;border:1px solid #1e3a5f">
        <b style="color:#38bdf8">📌 Rolling Average Guide</b><br>
        <span style="color:#94a3b8;font-size:0.85rem">
            • <b style='color:#38bdf8'>7-Day</b>: Smooths weekly noise — spot mid-term trends<br>
            • <b style='color:#fb923c'>30-Day</b>: Long-term seasonal pattern detection<br>
            • <b style='color:#475569'>Daily</b>: Raw revenue — shows full volatility
        </span>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("#### 📋 Monthly Revenue Breakdown")
    table = agg.copy()
    table["Growth %"] = table["revenue"].pct_change() * 100
    table = table.rename(columns={
        "month_year":"Month","revenue":"Revenue (₹)",
        "profit":"Profit (₹)","units":"Units","orders":"Records",
    })

    def color_growth(val):
        try:
            v = float(val)
            if v > 0:   return "color:#34d399"
            elif v < 0: return "color:#ef4444"
        except: pass
        return ""

    styled = (
        table[["Month","Revenue (₹)","Profit (₹)","Units","Records","Growth %"]]
        .style
        .format({"Revenue (₹)":"₹{:,.0f}","Profit (₹)":"₹{:,.0f}",
                 "Units":"{:,}","Records":"{:,}","Growth %":"{:+.1f}%"})
        .applymap(color_growth, subset=["Growth %"])
    )
    st.dataframe(styled, use_container_width=True, height=440)

with tab4:
    if df["year"].nunique() > 1:
        yoy = df.groupby(["year","month"])["revenue"].sum().reset_index()
        fig_yoy = px.line(
            yoy, x="month", y="revenue", color="year",
            color_discrete_sequence=["#38bdf8","#818cf8"],
            template="plotly_dark", markers=True,
            title="Year-over-Year Monthly Revenue",
            labels={"month":"Month","revenue":"Revenue (₹)","year":"Year"},
        )
        fig_yoy.update_layout(height=380, margin=dict(l=10,r=10,t=60,b=10))
        st.plotly_chart(fig_yoy, use_container_width=True)

        # YoY summary
        yoy_summary = df.groupby("year").agg(
            Revenue=("revenue","sum"),
            Profit=("profit","sum"),
            Units=("units_sold","sum"),
            Records=("revenue","count"),
        ).reset_index()
        yoy_summary["Margin %"] = (yoy_summary["Profit"] / yoy_summary["Revenue"] * 100).round(1)
        col1, col2 = st.columns(2)
        for i, row in yoy_summary.iterrows():
            (col1 if i == 0 else col2).markdown(f"""
            <div style="background:#1e293b;border-radius:12px;padding:18px 22px;border:1px solid #1e3a5f">
                <div style="color:#38bdf8;font-weight:700;font-size:1.1rem">📅 {int(row['year'])}</div>
                <div style="display:flex;gap:24px;margin-top:10px">
                    <div><div style="color:#94a3b8;font-size:0.72rem">REVENUE</div>
                         <div style="color:#f8fafc;font-weight:700">₹{row['Revenue']/1e6:.2f}M</div></div>
                    <div><div style="color:#94a3b8;font-size:0.72rem">PROFIT</div>
                         <div style="color:#34d399;font-weight:700">₹{row['Profit']/1e6:.2f}M</div></div>
                    <div><div style="color:#94a3b8;font-size:0.72rem">MARGIN</div>
                         <div style="color:#fbbf24;font-weight:700">{row['Margin %']:.1f}%</div></div>
                    <div><div style="color:#94a3b8;font-size:0.72rem">UNITS</div>
                         <div style="color:#f8fafc;font-weight:700">{int(row['Units']):,}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ YoY comparison requires data spanning multiple years.")
        st.plotly_chart(monthly_growth_chart(df), use_container_width=True)
