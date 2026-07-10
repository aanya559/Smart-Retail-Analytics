"""
pages/3_Store_Analysis.py — Updated for real dataset (store_name, department column)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import load_data, apply_sidebar_filters, compute_kpis
from utils.charts import (
    store_revenue_chart, heatmap_store_month,
    promotion_impact_chart, holiday_analysis_chart,
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

st.set_page_config(page_title="Store Analysis — Smart Retail", page_icon="🏪", layout="wide")
st.markdown(_CSS, unsafe_allow_html=True)

if st.session_state.get("df") is None:
    if os.path.exists("data/sales.csv"):
        st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.error("❌ data/sales.csv not found.")
        st.stop()

df_full = st.session_state["df"]
df = apply_sidebar_filters(df_full)

st.markdown("# 🏪 Store Analysis")
st.markdown("<p style='color:#64748b;margin-top:-12px'>Store performance · Heatmaps · Promotion & Holiday impact · Regional breakdown</p>",
            unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

store_agg = (
    df.groupby(["store_name","region"])
    .agg(revenue=("revenue","sum"), profit=("profit","sum"),
         orders=("revenue","count"), units=("units_sold","sum"))
    .reset_index().sort_values("revenue", ascending=False)
)

top_store = store_agg.iloc[0]
low_store = store_agg.iloc[-1]
avg_rev   = store_agg["revenue"].mean()

# ─── KPI Row ──────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("🏆 Top Store",      top_store["store_name"],     f"₹{top_store['revenue']/1e6:.2f}M")
c2.metric("⚠️ Lowest Store",  low_store["store_name"],     f"₹{low_store['revenue']/1e6:.2f}M")
c3.metric("📊 Avg Store Rev",  f"₹{avg_rev/1e6:.2f}M")
c4.metric("🏪 Active Stores",  df["store_id"].nunique())

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue by Store",
    "🔥 Revenue Heatmap",
    "🏷️ Promotion Impact",
    "🎉 Holiday Analysis",
])

with tab1:
    st.plotly_chart(store_revenue_chart(df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏆 Top 5 Stores")
        top5 = store_agg.head(5)[["store_name","region","revenue","profit","orders"]].copy()
        top5.columns = ["Store","Region","Revenue (₹)","Profit (₹)","Records"]
        st.dataframe(
            top5.style.format({"Revenue (₹)":"₹{:,.0f}","Profit (₹)":"₹{:,.0f}"}),
            use_container_width=True, hide_index=True,
        )
    with col2:
        st.markdown("#### ⚠️ Bottom 5 Stores")
        bot5 = store_agg.tail(5)[["store_name","region","revenue","profit","orders"]].copy()
        bot5.columns = ["Store","Region","Revenue (₹)","Profit (₹)","Records"]
        st.dataframe(
            bot5.style.format({"Revenue (₹)":"₹{:,.0f}","Profit (₹)":"₹{:,.0f}"}),
            use_container_width=True, hide_index=True,
        )

    st.markdown("#### 🌍 Revenue by Store — Coloured by Region")
    fig_reg = px.bar(
        store_agg, x="store_name", y="revenue", color="region",
        template="plotly_dark",
        color_discrete_sequence=["#38bdf8","#818cf8","#34d399","#fb923c"],
        labels={"revenue":"Revenue (₹)","store_name":"Store","region":"Region"},
        title="Store Revenue by Region",
    )
    fig_reg.update_layout(height=380, margin=dict(l=10,r=10,t=60,b=10))
    st.plotly_chart(fig_reg, use_container_width=True)

with tab2:
    st.plotly_chart(heatmap_store_month(df), use_container_width=True)

    # Region × Month heatmap
    st.markdown("#### 🌍 Revenue Heatmap — Region × Month")
    reg_pivot = df.pivot_table(
        values="revenue", index="region", columns="month", aggfunc="sum", fill_value=0
    )
    month_map = {i:m for i,m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],1)}
    reg_pivot.columns = [month_map.get(c,str(c)) for c in reg_pivot.columns]
    fig_rh = go.Figure(go.Heatmap(
        z=reg_pivot.values, x=reg_pivot.columns.tolist(), y=reg_pivot.index.tolist(),
        colorscale="Plasma",
        hovertemplate="Region: <b>%{y}</b><br>Month: <b>%{x}</b><br>Revenue: ₹%{z:,.0f}<extra></extra>",
    ))
    fig_rh.update_layout(template="plotly_dark", height=320,
                         margin=dict(l=60,r=10,t=40,b=10),
                         title="Region × Month Revenue")
    st.plotly_chart(fig_rh, use_container_width=True)

with tab3:
    st.plotly_chart(promotion_impact_chart(df), use_container_width=True)

    promo_s = df.groupby(["store_name","promotion"])["revenue"].mean().reset_index()
    promo_s["Label"] = promo_s["promotion"].map({1:"With Promo",0:"No Promo"})
    pivot_p = promo_s.pivot_table(values="revenue", index="store_name", columns="Label")
    if "With Promo" in pivot_p.columns and "No Promo" in pivot_p.columns:
        pivot_p["Lift %"] = ((pivot_p["With Promo"] - pivot_p["No Promo"]) / pivot_p["No Promo"] * 100).round(1)
        pivot_p = pivot_p.reset_index().rename(columns={"store_name":"Store"})
        st.markdown("#### 📋 Promotion Lift by Store")
        st.dataframe(
            pivot_p.style.format({
                "With Promo":"₹{:,.0f}","No Promo":"₹{:,.0f}","Lift %":"{:+.1f}%"
            }).background_gradient(subset=["Lift %"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True,
        )

with tab4:
    st.plotly_chart(holiday_analysis_chart(df), use_container_width=True)
    hol_mean    = df[df["holiday"]==1]["revenue"].mean() if df["holiday"].sum() > 0 else 0
    no_hol_mean = df[df["holiday"]==0]["revenue"].mean()
    if no_hol_mean > 0 and hol_mean > 0:
        multiplier = hol_mean / no_hol_mean
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:14px 18px;border:1px solid #1e3a5f;margin-top:8px">
            <b style="color:#f472b6">🎉 Holiday Effect Summary</b><br>
            <span style="color:#94a3b8;font-size:0.9rem">
                Holiday avg: <b style='color:#f8fafc'>₹{hol_mean:,.0f}</b> &nbsp;|&nbsp;
                Regular avg: <b style='color:#f8fafc'>₹{no_hol_mean:,.0f}</b> &nbsp;|&nbsp;
                Multiplier: <b style='color:#f472b6'>{multiplier:.2f}x</b>
            </span>
        </div>
        """, unsafe_allow_html=True)
