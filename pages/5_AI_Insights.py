"""
pages/5_AI_Insights.py — Updated for real dataset (economic indicators in prediction)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys, os, io, calendar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import load_data, apply_sidebar_filters, compute_kpis, load_model, generate_insights
from utils.charts import feature_importance_chart, next_month_forecast_chart

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
.stButton>button{background:linear-gradient(135deg,#0ea5e9,#6366f1);color:white !important;border:none;border-radius:8px;font-weight:600;padding:0.5rem 1.2rem;transition:opacity 0.2s,transform 0.2s;}
.stButton>button:hover{opacity:0.88;transform:translateY(-1px);}
::-webkit-scrollbar{width:6px;} ::-webkit-scrollbar-track{background:#0f172a;}
::-webkit-scrollbar-thumb{background:#334155;border-radius:4px;}
hr{border-color:#1e2d45;}
</style>
"""

st.set_page_config(page_title="AI Insights — Smart Retail", page_icon="🤖", layout="wide")
st.markdown(_CSS, unsafe_allow_html=True)

if st.session_state.get("df") is None:
    if os.path.exists("data/sales.csv"):
        st.session_state["df"] = load_data("data/sales.csv")
    else:
        st.error("❌ data/sales.csv not found.")
        st.stop()

df_full = st.session_state["df"]
df = apply_sidebar_filters(df_full)

st.markdown("# 🤖 AI Insights & ML Predictions")
st.markdown("<p style='color:#64748b;margin-top:-12px'>Automated business intelligence · ML forecasting · Feature analysis</p>",
            unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

tab1, tab2, tab3 = st.tabs([
    "🧠 Business Insights",
    "🤖 ML Prediction Simulator",
    "🔑 Feature Importance",
])

# ═══════════════════════════════════════════════
# TAB 1 — Business Insights
# ═══════════════════════════════════════════════
with tab1:
    st.markdown("### 🧠 Auto-Generated Business Insights")
    st.markdown("<p style='color:#64748b'>Rule-based insights derived from filtered data.</p>", unsafe_allow_html=True)
    st.markdown("---")

    insights = generate_insights(df)
    type_config = {
        "success": ("✅", "#064e3b", "#10b981", "#d1fae5"),
        "warning": ("⚠️", "#451a03", "#f59e0b", "#fef3c7"),
        "info":    ("💡", "#0c1a40", "#38bdf8", "#e0f2fe"),
        "error":   ("🚨", "#450a0a", "#ef4444", "#fee2e2"),
    }

    for ins in insights:
        itype = ins.get("type", "info")
        _, bg, border, _ = type_config.get(itype, type_config["info"])
        st.markdown(f"""
        <div style="background:{bg}44; border:1px solid {border}66; border-left:4px solid {border}; border-radius:10px; padding:14px 18px; margin-bottom:10px;">
            <div style="font-size:1rem;font-weight:600;color:#f8fafc">{ins['icon']} {ins['title']}</div>
            <div style="font-size:0.88rem;color:#cbd5e1;margin-top:4px">{ins['body']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    kpis = compute_kpis(df)
    c1.metric("💰 Total Revenue", f"₹{kpis['total_revenue']/1e6:.2f}M")
    c2.metric("📈 Profit Margin", f"{kpis['profit_margin']:.1f}%")
    c3.metric("📅 MoM Growth",    f"{kpis['mom_growth']:+.1f}%", delta_color="normal" if kpis['mom_growth']>=0 else "inverse")


# ═══════════════════════════════════════════════
# TAB 2 — ML Prediction Simulator
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("### 🤖 Advanced ML Simulator")
    
    model_payload = st.session_state.get("model_payload") or load_model("model/forecast.pkl")

    with st.expander("📤 Upload Custom model.pkl (optional)"):
        uploaded = st.file_uploader("Upload a trained joblib model", type=["pkl"])
        if uploaded is not None:
            import joblib
            try:
                model_payload = joblib.load(io.BytesIO(uploaded.read()))
                st.session_state["model_payload"] = model_payload
                st.success("✅ Custom model loaded successfully!")
            except Exception as e:
                st.error(f"❌ Failed to load model: {e}")

    if model_payload is None:
        st.warning("⚠️ No model found. Please run `python train_model.py` and restart the app.")
    else:
        model     = model_payload["model"]
        metrics   = model_payload.get("metrics", {})
        feat_cols = model_payload.get("feature_cols", [])
        encoders  = model_payload.get("encoders", {})

        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Model R² Score", f"{metrics.get('R2', '?')}")
        c2.metric("📉 Mean Abs Error (MAE)", f"₹{metrics.get('MAE', 0):,}")
        c3.metric("📉 Root Mean Sq Error", f"₹{metrics.get('RMSE', 0):,}")

        st.markdown("---")
        st.markdown("#### ⚙️ Simulation Parameters")

        col1, col2, col3 = st.columns(3)
        with col1:
            pred_store    = st.selectbox("Store", sorted(df["store_name"].unique()))
            pred_region   = st.selectbox("Region", sorted(df["region"].unique()))
        with col2:
            pred_category = st.selectbox("Category", sorted(df["category"].unique()))
            pred_dept     = st.selectbox("Department", sorted(df["department"].unique()))
        with col3:
            pred_temp     = st.slider("Temperature (°C)", 0.0, 45.0, 25.0)
            pred_cpi      = st.slider("CPI (Inflation)", 180.0, 260.0, 220.0)

        c1, c2, c3 = st.columns(3)
        with c1: pred_fuel = st.number_input("Fuel Price", 2.0, 6.0, 3.5, 0.1)
        with c2: pred_unemp= st.number_input("Unemployment %", 2.0, 15.0, 6.0, 0.1)
        with c3: 
            st.markdown("<br>", unsafe_allow_html=True)
            pred_promo   = st.checkbox("Include Promotion", value=True)
            pred_holiday = st.checkbox("Mark as Holiday Period", value=False)

        if st.button("🔮 Run 3-Month Forecast Simulation", use_container_width=True):
            from datetime import date
            import calendar as cal
            today = date.today()
            
            # Approximating base units_sold for this category/dept combo
            mask_cat = (df["category"] == pred_category) & (df["department"] == pred_dept)
            base_units = df[mask_cat]["units_sold"].mean()
            if pd.isna(base_units): base_units = df["units_sold"].mean()
            
            predictions, ci_low, ci_high, labels = [], [], [], []
            for i in range(1, 4):
                m = (today.month + i - 1) % 12 + 1
                y = today.year + (today.month + i - 1) // 12
                
                row = {
                    "year": y, "month": m, "quarter": (m - 1) // 3 + 1,
                    "day_of_week": 2, "week_of_year": 26,
                    "units_sold": int(base_units),
                    "promotion": int(pred_promo), "holiday": int(pred_holiday),
                    "temperature": pred_temp, "fuel_price": pred_fuel,
                    "cpi": pred_cpi, "unemployment": pred_unemp,
                }
                
                # Encoding
                try: row["region_enc"] = encoders["region"].transform([pred_region])[0]
                except: row["region_enc"] = 0
                try: row["category_enc"] = encoders["category"].transform([pred_category])[0]
                except: row["category_enc"] = 0
                try: row["department_enc"] = encoders["department"].transform([pred_dept])[0]
                except: row["department_enc"] = 0
                
                # store_id in the CSV is already "Store 01" format
                try: row["store_enc"] = encoders["store"].transform([pred_store])[0]
                except: row["store_enc"] = 0

                X_pred = pd.DataFrame([row])[feat_cols]
                
                pred = model.predict(X_pred)[0]
                # CI estimate
                if hasattr(model, "estimators_"):
                    tree_preds = np.array([t.predict(X_pred)[0] for t in model.estimators_])
                    std = tree_preds.std()
                else:
                    std = pred * 0.10
                    
                predictions.append(round(pred, 2))
                ci_low.append(round(max(0, pred - 1.65 * std), 2))
                ci_high.append(round(pred + 1.65 * std, 2))
                labels.append(f"{cal.month_abbr[m]} {y}")

            st.plotly_chart(
                next_month_forecast_chart(labels, predictions, ci_low, ci_high),
                use_container_width=True
            )
            
            st.success(f"📈 Simulated 3-month total revenue: **₹{sum(predictions):,.2f}**")


# ═══════════════════════════════════════════════
# TAB 3 — Feature Importance
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("### 🔑 Feature Importance Analysis")
    model_payload = st.session_state.get("model_payload")
    
    if model_payload and "feature_importance" in model_payload:
        st.plotly_chart(
            feature_importance_chart(model_payload["feature_importance"]),
            use_container_width=True
        )

        imp = model_payload["feature_importance"]
        top_feat = max(imp, key=imp.get)
        
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:12px;padding:18px 22px;border:1px solid #1e3a5f;margin-bottom:10px">
            <b style="color:#38bdf8">🔑 Primary Driver</b><br>
            <span style="color:#f8fafc;font-size:1rem"><b>{top_feat}</b> is the strongest predictor of revenue.</span><br>
            <span style="color:#94a3b8;font-size:0.85rem">
                This indicates that out of all macroeconomic, seasonal, and categorical variables,
                {top_feat} holds the most weight in the Random Forest model's decision splits.
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Train the model first (`python train_model.py`) to see feature importance.")
