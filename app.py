"""
app.py — Main entry point for Smart Retail Analytics Dashboard
"""
import streamlit as st

st.set_page_config(
    page_title="Smart Retail Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Global dark-mode CSS + custom styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset & base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #080f1a; color: #f1f5f9; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #111c30 100%) !important;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h3 { color: #38bdf8 !important; }

/* Hide default Streamlit menu / footer */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 18px 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(56,189,248,0.15);
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { color: #f8fafc !important; font-size: 1.5rem; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* Page title */
h1 { color: #38bdf8 !important; font-weight: 700 !important; }
h2 { color: #e2e8f0 !important; font-weight: 600 !important; }
h3 { color: #cbd5e1 !important; font-weight: 500 !important; }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #0f172a;
    border-radius: 8px;
    padding: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #94a3b8 !important;
    border-radius: 6px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #38bdf8 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: opacity 0.2s, transform 0.2s;
}
.stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

/* Select / multiselect */
[data-baseweb="select"] > div {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #f1f5f9 !important;
}

/* Divider */
hr { border-color: #1e2d45; }

/* Plotly chart container */
.stPlotlyChart {
    background: #0f172a;
    border-radius: 14px;
    border: 1px solid #1e2d45;
    padding: 4px;
}

/* Info / success / warning boxes */
.stAlert {
    border-radius: 10px;
    border-left-width: 4px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

/* Data table */
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Bootstrap session state with data + model
# ─────────────────────────────────────────────
from utils.helper import load_data, load_model
import os

if "df" not in st.session_state:
    if os.path.exists("data/sales.csv"):
        with st.spinner("⚡ Loading retail data…"):
            st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.session_state["df"] = None

if "model_payload" not in st.session_state:
    st.session_state["model_payload"] = load_model("model/forecast.pkl")

# ─────────────────────────────────────────────
# Landing hero (shown only on app.py itself)
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #ec4899 100%);
    border-radius: 18px;
    padding: 40px 48px;
    margin-bottom: 28px;
    box-shadow: 0 8px 40px rgba(14,165,233,0.3);
">
    <div style="font-size:2.6rem;font-weight:800;color:white;letter-spacing:-0.02em">
        🛒 Smart Retail Analytics
    </div>
    <div style="font-size:1.05rem;color:rgba(255,255,255,0.88);margin-top:10px;max-width:540px">
        A portfolio-grade, multi-page sales forecasting dashboard powered by
        RandomForest ML, interactive Plotly charts, and AI-generated business insights.
    </div>
    <div style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap">
        <span style="background:rgba(255,255,255,0.18);border-radius:20px;padding:4px 14px;font-size:0.82rem;color:white">
            📊 5,000+ Transactions
        </span>
        <span style="background:rgba(255,255,255,0.18);border-radius:20px;padding:4px 14px;font-size:0.82rem;color:white">
            🏪 20 Stores · 5 Regions · 25 Departments
        </span>
        <span style="background:rgba(255,255,255,0.18);border-radius:20px;padding:4px 14px;font-size:0.82rem;color:white">
            🤖 RandomForest Forecast
        </span>
        <span style="background:rgba(255,255,255,0.18);border-radius:20px;padding:4px 14px;font-size:0.82rem;color:white">
            🧠 AI Insights
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Quick Nav cards
# ─────────────────────────────────────────────
st.markdown("### 📌 Navigate to a Page")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("📊 Overview", use_container_width=True):
        st.switch_page("pages/1_Overview.py")
    st.caption("KPIs, trends & category breakdown")

with c2:
    if st.button("📅 Forecasting", use_container_width=True):
        st.switch_page("pages/2_Forecasting.py")
    st.caption("Actual vs forecast + rolling avg")

with c3:
    if st.button("🏪 Store Analysis", use_container_width=True):
        st.switch_page("pages/3_Store_Analysis.py")
    st.caption("Store performance & heatmaps")

with c4:
    if st.button("📦 Product Analysis", use_container_width=True):
        st.switch_page("pages/4_Product_Analysis.py")
    st.caption("Top products & scatter analysis")

with c5:
    if st.button("🤖 AI Insights", use_container_width=True):
        st.switch_page("pages/5_AI_Insights.py")
    st.caption("ML predictions & business insights")

# ─────────────────────────────────────────────
# Data status
# ─────────────────────────────────────────────
st.markdown("---")
df = st.session_state.get("df")
model_payload = st.session_state.get("model_payload")

c1, c2, c3 = st.columns(3)
if df is not None:
    c1.success(f"✅ Data loaded — **{len(df):,} rows** ready")
    c2.info(f"📅 Date range: **{df['date'].min().date()}** → **{df['date'].max().date()}**")
else:
    c1.error("❌ `data/sales.csv` not found. Run `python generate_data.py` first.")

if model_payload:
    m = model_payload.get("metrics", {})
    c3.success(f"🤖 Model loaded — R²: **{m.get('R2', '?')}** | MAE: ₹**{m.get('MAE', '?'):,}**")
else:
    c3.warning("⚠️ No model found. Run `python train_model.py` to generate one.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit · Plotly · Scikit-learn · Pandas")
