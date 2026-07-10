"""
pages/4_Product_Analysis.py — Updated for real dataset (department drill-down, economic context)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import load_data, apply_sidebar_filters, compute_kpis
from utils.charts import (
    top_departments_chart, scatter_profit_revenue, donut_chart,
    economic_indicators_chart
)

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
</style>
"""

st.set_page_config(page_title="Department Analysis — Smart Retail", page_icon="🏬", layout="wide")
st.markdown(_CSS, unsafe_allow_html=True)

if st.session_state.get("df") is None:
    if os.path.exists("data/sales.csv"):
        st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.error("❌ data/sales.csv not found.")
        st.stop()

df_full = st.session_state["df"]
df = apply_sidebar_filters(df_full)

st.markdown("# 🏬 Department & Category Analysis")
st.markdown("<p style='color:#64748b;margin-top:-12px'>Top departments · Profit vs Revenue · Category deep-dive · Economic impact</p>",
            unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

dept_agg = df.groupby("department")["revenue"].sum()
top_dept = dept_agg.idxmax()
top_dept_rev = dept_agg.max()

cat_agg = df.groupby("category")["profit"].sum()
top_cat = cat_agg.idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔥 Top Department", top_dept,               f"₹{top_dept_rev/1e6:.2f}M rev")
c2.metric("🏆 Top Category",  top_cat,                f"₹{cat_agg.max()/1e6:.2f}M profit")
c3.metric("🏬 Unique Depts",  df["department"].nunique())
c4.metric("💰 Avg Unit Price", f"₹{df['unit_price'].mean():,.0f}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Top Departments",
    "📊 Profit vs Revenue",
    "🛒 Category Deep-Dive",
    "📈 Economic Impact",
])

with tab1:
    n_depts = st.slider("Number of departments to show", 3, 10, 10)
    st.plotly_chart(top_departments_chart(df, n=n_depts), use_container_width=True)

    with st.expander("📋 Department Summary Table"):
        dept_table = (
            df.groupby(["department","category"])
            .agg(revenue=("revenue","sum"), profit=("profit","sum"),
                 units=("units_sold","sum"), orders=("revenue","count"))
            .reset_index().sort_values("revenue", ascending=False)
        )
        dept_table.columns = ["Department","Category","Revenue (₹)","Profit (₹)","Units","Orders"]
        dept_table["Margin %"] = (dept_table["Profit (₹)"] / dept_table["Revenue (₹)"] * 100).round(1)
        st.dataframe(
            dept_table.style.format({
                "Revenue (₹)":"₹{:,.0f}","Profit (₹)":"₹{:,.0f}","Margin %":"{:.1f}%"
            }).background_gradient(subset=["Margin %"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True,
        )

with tab2:
    st.plotly_chart(scatter_profit_revenue(df), use_container_width=True)

    st.markdown("#### 📈 Units Sold vs Revenue by Category")
    fig_uv = px.scatter(
        df.sample(min(2000, len(df)), random_state=1),
        x="units_sold", y="revenue", color="category",
        facet_col="category", facet_col_wrap=3,
        color_discrete_sequence=["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6"],
        template="plotly_dark", opacity=0.65,
        labels={"units_sold":"Units Sold","revenue":"Revenue (₹)"},
        title="Units Sold vs Revenue — by Category",
    )
    fig_uv.update_layout(height=520, margin=dict(l=10,r=10,t=80,b=10), showlegend=False)
    st.plotly_chart(fig_uv, use_container_width=True)

with tab3:
    selected_cat = st.selectbox("Select Category", sorted(df["category"].unique()))
    cat_df = df[df["category"] == selected_cat]

    col1, col2 = st.columns(2)
    # Department Breakdown
    dept_pie = cat_df.groupby("department")["revenue"].sum().reset_index()
    fig_pie = px.pie(
        dept_pie, values="revenue", names="department", hole=0.45,
        template="plotly_dark",
        color_discrete_sequence=["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6"],
        title=f"Department Revenue Share — {selected_cat}",
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label")
    fig_pie.update_layout(height=380, margin=dict(l=10,r=10,t=60,b=10))
    col1.plotly_chart(fig_pie, use_container_width=True)

    # Monthly Trend
    cat_trend = cat_df.groupby("month_year")["revenue"].sum().reset_index()
    fig_trend = px.area(
        cat_trend, x="month_year", y="revenue",
        template="plotly_dark", color_discrete_sequence=["#38bdf8"],
        title=f"Monthly Revenue — {selected_cat}",
        labels={"month_year":"Month","revenue":"Revenue (₹)"},
    )
    fig_trend.update_layout(height=380, margin=dict(l=10,r=10,t=60,b=10))
    col2.plotly_chart(fig_trend, use_container_width=True)

    cat_rev    = cat_df["revenue"].sum()
    cat_profit = cat_df["profit"].sum()
    cat_units  = cat_df["units_sold"].sum()
    cat_orders = len(cat_df)

    st.markdown(f"""
    <div style="background:#1e293b;border-radius:12px;padding:18px 22px;border:1px solid #1e3a5f;margin-top:8px;display:flex;gap:32px;flex-wrap:wrap">
        <div><div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase">Revenue</div>
             <div style="color:#f8fafc;font-size:1.2rem;font-weight:700">₹{cat_rev/1e6:.2f}M</div></div>
        <div><div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase">Profit</div>
             <div style="color:#34d399;font-size:1.2rem;font-weight:700">₹{cat_profit/1e6:.2f}M</div></div>
        <div><div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase">Margin</div>
             <div style="color:#fbbf24;font-size:1.2rem;font-weight:700">{cat_profit/cat_rev*100:.1f}%</div></div>
        <div><div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase">Orders</div>
             <div style="color:#f8fafc;font-size:1.2rem;font-weight:700">{cat_orders:,}</div></div>
        <div><div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase">Units</div>
             <div style="color:#f8fafc;font-size:1.2rem;font-weight:700">{cat_units:,}</div></div>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("#### 🌍 Macro-Economic Factors vs Sales")
    st.markdown("Analyze how Temperature, Fuel Price, CPI, and Unemployment influence sales volumes.")

    # Using the new economic indicators chart
    if "temperature" in df.columns:
        st.plotly_chart(economic_indicators_chart(df), use_container_width=True)
    else:
        st.info("Economic data columns missing from dataset.")

    with st.expander("📊 Correlation Matrix (Economics)"):
        econ_cols = ["revenue", "profit", "units_sold", "temperature", "fuel_price", "cpi", "unemployment"]
        corr = df[econ_cols].corr().round(3)

        fig_corr = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu", zmin=-1, zmax=1,
            text=corr.values, texttemplate="%{text}", textfont={"size":10},
        ))
        fig_corr.update_layout(template="plotly_dark", height=400, margin=dict(l=40,r=10,t=40,b=10))
        st.plotly_chart(fig_corr, use_container_width=True)
