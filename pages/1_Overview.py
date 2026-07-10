"""
pages/1_Overview.py — Updated for real dataset schema
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import load_data, apply_sidebar_filters, compute_kpis
from utils.charts import (
    sales_trend_chart, category_bar_chart, donut_chart,
    region_treemap, monthly_growth_chart, department_bar_chart,
)

st.set_page_config(page_title="Overview — Smart Retail", page_icon="📊", layout="wide")

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #080f1a; color: #f1f5f9; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1424,#111c30) !important; border-right: 1px solid #1e2d45; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h3 { color: #38bdf8 !important; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    border: 1px solid #1e3a5f; border-radius: 14px;
    padding: 18px 16px !important; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(56,189,248,0.15); }
[data-testid="stMetricLabel"] { color:#94a3b8 !important; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; }
[data-testid="stMetricValue"] { color:#f8fafc !important; font-size:1.5rem; font-weight:700; }
h1{color:#38bdf8 !important;font-weight:700 !important;} h2{color:#e2e8f0 !important;} h3{color:#cbd5e1 !important;}
.stPlotlyChart{background:#0f172a;border-radius:14px;border:1px solid #1e2d45;padding:4px;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:#0f172a;border-radius:8px;padding:4px;}
[data-testid="stTabs"] [data-baseweb="tab"]{color:#94a3b8 !important;border-radius:6px;}
[data-testid="stTabs"] [aria-selected="true"]{background:#1e3a5f !important;color:#38bdf8 !important;}
::-webkit-scrollbar{width:6px;} ::-webkit-scrollbar-track{background:#0f172a;}
::-webkit-scrollbar-thumb{background:#334155;border-radius:4px;}
hr{border-color:#1e2d45;}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# ─── Load ──────────────────────────────────
if st.session_state.get("df") is None:
    if os.path.exists("data/sales.csv"):
        st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.error("❌ data/sales.csv not found.")
        st.stop()

df_full = st.session_state["df"]
df = apply_sidebar_filters(df_full)

st.markdown("# 📊 Overview Dashboard")
st.markdown("<p style='color:#64748b;margin-top:-12px'>Retail performance summary · 2022–2024 · 20 Stores · 5 Categories</p>",
            unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

kpis = compute_kpis(df)
mom  = kpis["mom_growth"]

# ─── KPI Row ──────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💰 Total Revenue",    f"₹{kpis['total_revenue']/1e6:.2f}M",  f"{mom:+.1f}% MoM")
c2.metric("📈 Total Profit",     f"₹{kpis['total_profit']/1e6:.2f}M",   f"{kpis['profit_margin']:.1f}% margin")
c3.metric("🛒 Total Records",    f"{kpis['total_orders']:,}")
c4.metric("🏪 Active Stores",    f"{kpis['num_stores']}")
c5.metric("📦 Units Sold",       f"{kpis['total_units']:,}")
c6.metric("🎯 Avg Revenue/Day",  f"₹{kpis['avg_order_val']:,.0f}")

st.markdown("---")

# ─── Monthly Trend ────────────────────────
st.plotly_chart(sales_trend_chart(df), use_container_width=True)

# ─── Category + Donut ─────────────────────
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(category_bar_chart(df), use_container_width=True)
with col2:
    st.plotly_chart(donut_chart(df, "category"), use_container_width=True)

# ─── Department Bar + Region Donut ────────
col3, col4 = st.columns([3, 2])
with col3:
    st.plotly_chart(department_bar_chart(df), use_container_width=True)
with col4:
    st.plotly_chart(donut_chart(df, "region"), use_container_width=True)

# ─── Region Treemap ───────────────────────
st.plotly_chart(region_treemap(df), use_container_width=True)

# ─── Monthly Growth ───────────────────────
st.plotly_chart(monthly_growth_chart(df), use_container_width=True)

# ─── Summary Table ────────────────────────
with st.expander("📋 Monthly Revenue Summary Table"):
    monthly = (
        df.groupby("month_year")
        .agg(Revenue=("revenue","sum"), Profit=("profit","sum"),
             Orders=("revenue","count"), Units=("units_sold","sum"))
        .reset_index().rename(columns={"month_year":"Month"})
    )
    monthly["Margin %"] = (monthly["Profit"] / monthly["Revenue"] * 100).round(1)
    st.dataframe(
        monthly.style.format({
            "Revenue": "₹{:,.0f}", "Profit": "₹{:,.0f}", "Margin %": "{:.1f}%",
        }),
        use_container_width=True,
    )
