"""
utils/charts.py — Updated for real dataset schema
Columns: date, store_id, store_name, region, category, department,
         holiday, temperature, fuel_price, cpi, unemployment,
         promotion, units_sold, revenue, profit, unit_price, month_year
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.helper import monthly_agg, rolling_avg, color_scale

TEMPLATE = "plotly_dark"
COLORS   = color_scale()
ACCENT   = "#38bdf8"
ACCENT2  = "#818cf8"
WARN     = "#fb923c"
SUCCESS  = "#34d399"


# ─────────────────────────────────────────────
# Monthly Sales Trend
# ─────────────────────────────────────────────
def sales_trend_chart(df: pd.DataFrame, show_rolling: bool = True) -> go.Figure:
    agg = monthly_agg(df)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=agg["month_year"], y=agg["revenue"],
        mode="lines+markers", name="Revenue",
        line=dict(color=ACCENT, width=2.5), marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))

    if show_rolling and len(agg) >= 3:
        ra = rolling_avg(agg["revenue"], 3)
        fig.add_trace(go.Scatter(
            x=agg["month_year"], y=ra,
            mode="lines", name="3-Month Rolling Avg",
            line=dict(color=SUCCESS, width=1.8, dash="dash"),
            hovertemplate="<b>%{x}</b><br>Rolling Avg: ₹%{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        template=TEMPLATE,
        title=dict(text="📈 Monthly Revenue Trend", font=dict(size=16)),
        xaxis_title="Month", yaxis_title="Revenue (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380, margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Category Bar
# ─────────────────────────────────────────────
def category_bar_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("category")["revenue"].sum().sort_values().reset_index()
    fig = px.bar(
        agg, x="revenue", y="category", orientation="h",
        color="category", color_discrete_sequence=COLORS,
        template=TEMPLATE, title="📊 Revenue by Category",
        text=agg["revenue"].apply(lambda x: f"₹{x/1e6:.2f}M"),
        labels={"revenue": "Revenue (₹)", "category": ""},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=360,
                      margin=dict(l=10, r=70, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Department Bar
# ─────────────────────────────────────────────
def department_bar_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("department")["revenue"].sum().sort_values().reset_index()
    fig = px.bar(
        agg, x="revenue", y="department", orientation="h",
        color="revenue", color_continuous_scale="Blues",
        template=TEMPLATE, title="🏬 Revenue by Department",
        text=agg["revenue"].apply(lambda x: f"₹{x/1e6:.2f}M"),
        labels={"revenue": "Revenue (₹)", "department": ""},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=380,
                      margin=dict(l=10, r=70, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Donut Chart
# ─────────────────────────────────────────────
def donut_chart(df: pd.DataFrame, group_col: str = "category") -> go.Figure:
    agg = df.groupby(group_col)["revenue"].sum().reset_index()
    fig = px.pie(
        agg, values="revenue", names=group_col,
        hole=0.52, color_discrete_sequence=COLORS,
        template=TEMPLATE, title=f"🍩 Revenue Share — {group_col.title()}",
    )
    fig.update_traces(
        textposition="outside", textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Region Treemap
# ─────────────────────────────────────────────
def region_treemap(df: pd.DataFrame) -> go.Figure:
    agg = (
        df.groupby(["region", "category"])
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    fig = px.treemap(
        agg, path=["region", "category"], values="revenue",
        color="profit", color_continuous_scale="RdYlGn",
        template=TEMPLATE, title="🌍 Revenue by Region & Category",
        hover_data={"revenue": ":,.0f", "profit": ":,.0f"},
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Top Products / Departments
# ─────────────────────────────────────────────
def top_departments_chart(df: pd.DataFrame, n: int = 10) -> go.Figure:
    agg = (
        df.groupby(["department", "category"])["revenue"]
        .sum().nlargest(n).reset_index().sort_values("revenue")
    )
    fig = px.bar(
        agg, x="revenue", y="department", orientation="h",
        color="category", color_discrete_sequence=COLORS,
        template=TEMPLATE, title=f"🔥 Top {n} Departments by Revenue",
        text=agg["revenue"].apply(lambda x: f"₹{x/1e6:.2f}M"),
        labels={"revenue": "Revenue (₹)", "department": ""},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420, margin=dict(l=10, r=80, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Scatter: Profit vs Revenue
# ─────────────────────────────────────────────
def scatter_profit_revenue(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample, x="revenue", y="profit",
        color="category", size="units_sold",
        hover_data=["store_name", "department", "region"],
        color_discrete_sequence=COLORS,
        template=TEMPLATE, title="📊 Profit vs Revenue",
        opacity=0.72,
        labels={"revenue": "Revenue (₹)", "profit": "Profit (₹)"},
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Heatmap: Store × Month
# ─────────────────────────────────────────────
def heatmap_store_month(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(
        values="revenue", index="store_name",
        columns="month", aggfunc="sum", fill_value=0,
    )
    month_names = {i: m for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1
    )}
    pivot.columns = [month_names.get(c, str(c)) for c in pivot.columns]

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale="Viridis",
        hovertemplate="Store: <b>%{y}</b><br>Month: <b>%{x}</b><br>Revenue: ₹%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Revenue (₹)"),
    ))
    fig.update_layout(
        template=TEMPLATE, title="🔥 Revenue Heatmap — Store × Month",
        xaxis_title="Month", yaxis_title="Store",
        height=500, margin=dict(l=80, r=20, t=60, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Forecast Chart (actual vs RF predicted)
# ─────────────────────────────────────────────
def forecast_chart(df: pd.DataFrame) -> go.Figure:
    agg = monthly_agg(df)
    std = agg["revenue"].std() * 0.10

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.concat([agg["month_year"], agg["month_year"].iloc[::-1]]),
        y=pd.concat([(agg["revenue"] * 1.08), (agg["revenue"] * 0.92).iloc[::-1]]),
        fill="toself", fillcolor="rgba(251,146,60,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=True, name="Confidence Band", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=agg["month_year"], y=agg["revenue"],
        mode="lines+markers", name="Actual Revenue",
        line=dict(color=ACCENT, width=2.5), marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Actual: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        template=TEMPLATE, title="📅 Monthly Revenue with Forecast Band",
        xaxis_title="Month", yaxis_title="Revenue (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400, margin=dict(l=10, r=10, t=70, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Promotion Impact
# ─────────────────────────────────────────────
def promotion_impact_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["category", "promotion"])["revenue"].mean().reset_index()
    agg["Promotion"] = agg["promotion"].map({1: "With Promotion", 0: "No Promotion"})
    fig = px.bar(
        agg, x="category", y="revenue", color="Promotion",
        barmode="group",
        color_discrete_map={"With Promotion": SUCCESS, "No Promotion": "#475569"},
        template=TEMPLATE, title="🏷️ Promotion Impact by Category",
        labels={"revenue": "Avg Revenue (₹)", "category": "Category"},
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Holiday Analysis
# ─────────────────────────────────────────────
def holiday_analysis_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["category", "holiday"])["revenue"].mean().reset_index()
    agg["Holiday"] = agg["holiday"].map({1: "Holiday", 0: "Regular Day"})
    fig = px.bar(
        agg, x="category", y="revenue", color="Holiday",
        barmode="group",
        color_discrete_map={"Holiday": "#f472b6", "Regular Day": "#475569"},
        template=TEMPLATE, title="🎉 Holiday vs Regular Day Revenue",
        labels={"revenue": "Avg Revenue (₹)", "category": "Category"},
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Monthly Growth %
# ─────────────────────────────────────────────
def monthly_growth_chart(df: pd.DataFrame) -> go.Figure:
    agg = monthly_agg(df)
    agg["growth"] = agg["revenue"].pct_change() * 100
    agg = agg.dropna(subset=["growth"])

    colors = [SUCCESS if g >= 0 else "#ef4444" for g in agg["growth"]]
    fig = go.Figure(go.Bar(
        x=agg["month_year"], y=agg["growth"],
        marker_color=colors,
        text=agg["growth"].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Growth: %{y:+.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="solid", line_color="#475569", line_width=1)
    fig.update_layout(
        template=TEMPLATE, title="📈 Monthly Revenue Growth %",
        xaxis_title="Month", yaxis_title="Growth (%)",
        height=360, margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Store Revenue
# ─────────────────────────────────────────────
def store_revenue_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("store_name")["revenue"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(
        agg, x="store_name", y="revenue",
        color="revenue", color_continuous_scale="Blues",
        template=TEMPLATE, title="🏪 Revenue by Store",
        text=agg["revenue"].apply(lambda x: f"₹{x/1e6:.2f}M"),
        labels={"revenue": "Revenue (₹)", "store_name": "Store"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=420,
                      margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Rolling Average Chart
# ─────────────────────────────────────────────
def rolling_avg_chart(df: pd.DataFrame) -> go.Figure:
    daily = df.groupby("date")["revenue"].sum().reset_index().sort_values("date")
    daily["ra_7"]  = rolling_avg(daily["revenue"], 7)
    daily["ra_30"] = rolling_avg(daily["revenue"], 30)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["revenue"],
        mode="lines", name="Daily Revenue",
        line=dict(color="#334155", width=1), opacity=0.5,
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["ra_7"],
        mode="lines", name="7-Day Rolling Avg",
        line=dict(color=ACCENT, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["ra_30"],
        mode="lines", name="30-Day Rolling Avg",
        line=dict(color=WARN, width=2.5),
    ))
    fig.update_layout(
        template=TEMPLATE, title="📉 Daily Revenue + Rolling Averages",
        xaxis_title="Date", yaxis_title="Revenue (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400, margin=dict(l=10, r=10, t=70, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Economic Indicators Chart
# ─────────────────────────────────────────────
def economic_indicators_chart(df: pd.DataFrame) -> go.Figure:
    daily = df.groupby("date").agg(
        revenue=("revenue", "sum"),
        temperature=("temperature", "mean"),
        cpi=("cpi", "mean"),
        fuel_price=("fuel_price", "mean"),
        unemployment=("unemployment", "mean"),
    ).reset_index().sort_values("date")

    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Temperature vs Revenue", "CPI vs Revenue",
                        "Fuel Price Trend", "Unemployment Rate"),
        shared_xaxes=False,
    )

    fig.add_trace(go.Scatter(x=daily["temperature"], y=daily["revenue"],
                             mode="markers", marker=dict(color=ACCENT, size=4, opacity=0.5),
                             name="Temp vs Rev"), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["cpi"], y=daily["revenue"],
                             mode="markers", marker=dict(color=ACCENT2, size=4, opacity=0.5),
                             name="CPI vs Rev"), row=1, col=2)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["fuel_price"],
                             mode="lines", line=dict(color=WARN, width=1.5),
                             name="Fuel Price"), row=2, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["unemployment"],
                             mode="lines", line=dict(color="#f472b6", width=1.5),
                             name="Unemployment"), row=2, col=2)

    fig.update_layout(
        template=TEMPLATE, title="📊 Economic Indicators",
        height=520, showlegend=False,
        margin=dict(l=10, r=10, t=80, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Feature Importance
# ─────────────────────────────────────────────
def feature_importance_chart(importance_dict: dict) -> go.Figure:
    df_imp = (
        pd.DataFrame.from_dict(importance_dict, orient="index", columns=["importance"])
        .sort_values("importance").reset_index()
        .rename(columns={"index": "feature"})
    )
    fig = px.bar(
        df_imp, x="importance", y="feature", orientation="h",
        color="importance", color_continuous_scale="Blues",
        template=TEMPLATE, title="🔑 Feature Importance (RandomForest)",
        labels={"importance": "Importance Score", "feature": "Feature"},
    )
    fig.update_layout(coloraxis_showscale=False, height=420,
                      margin=dict(l=10, r=10, t=60, b=10))
    return fig


# ─────────────────────────────────────────────
# Next Month Forecast Bar
# ─────────────────────────────────────────────
def next_month_forecast_chart(months, predictions, ci_low, ci_high) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=predictions, name="Predicted Revenue",
        marker_color=ACCENT,
        text=[f"₹{v:,.0f}" for v in predictions],
        textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=months + months[::-1],
        y=ci_high + ci_low[::-1],
        fill="toself", fillcolor="rgba(56,189,248,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="90% Confidence Interval", hoverinfo="skip",
    ))
    fig.update_layout(
        template=TEMPLATE, title="🤖 Next 3 Month Revenue Forecast",
        xaxis_title="Month", yaxis_title="Predicted Revenue (₹)",
        height=380, margin=dict(l=10, r=10, t=60, b=30),
    )
    return fig
