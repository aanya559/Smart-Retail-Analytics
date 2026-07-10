# Smart Retail Analytics & Sales Forecasting Dashboard

A portfolio-ready, fully interactive multi-page analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

---

## 🚀 Features

| Module | Highlights |
|---|---|
| **Overview** | KPI cards, monthly trend, category bars, donut share, region treemap, growth % |
| **Forecasting** | Actual vs forecast line chart, confidence intervals, rolling 7d/30d averages |
| **Store Analysis** | Revenue by store, heatmap (store × month), promotion & holiday impact |
| **Product Analysis** | Top 10 products, profit vs revenue scatter, category deep-dive |
| **AI Insights** | Auto-generated business insights, ML feature importance, next-month prediction |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit ≥1.35** — multi-page app framework
- **Pandas / NumPy** — data wrangling & synthetic data generation
- **Plotly ≥5.18** — interactive charts
- **Scikit-learn** — RandomForest forecast model
- **Joblib** — model serialization

---

## 📁 Folder Structure

```
Smart Retail Analytics/
├── app.py                      # Main entry point + sidebar + global CSS
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Forecasting.py
│   ├── 3_Store_Analysis.py
│   ├── 4_Product_Analysis.py
│   └── 5_AI_Insights.py
├── data/
│   └── sales.csv               # 5000-row synthetic retail dataset
├── model/
│   └── forecast.pkl            # Trained RandomForest model
├── utils/
│   ├── helper.py               # Data loading, filters, KPIs, insights
│   └── charts.py               # All Plotly chart builders
├── assets/
│   └── logo.png
├── generate_data.py            # Run once to regenerate data
├── train_model.py              # Run once to retrain model
└── requirements.txt
```

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate synthetic data

```bash
python generate_data.py
```

### 3. Train the forecast model

```bash
python train_model.py
```

### 4. Launch the dashboard

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📊 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Transaction date (2022–2024) |
| `store_id` | str | Store name (Store 01–20) |
| `region` | str | North/South/East/West/Central |
| `category` | str | Electronics/Food & Grocery/Furniture/Fashion/Home & Living |
| `product` | str | Product name |
| `units_sold` | int | Units sold (Poisson-distributed) |
| `unit_price` | float | Price per unit |
| `revenue` | float | Total revenue |
| `profit` | float | Profit (margin-adjusted) |
| `promotion` | int | 1 = promotion active, 0 = regular |
| `holiday` | int | 1 = holiday, 0 = regular day |
| `discount` | float | Discount rate (0–0.25) |
| `forecast` | float | Model forecast reference |

---

## 🤖 ML Model

- **Algorithm**: RandomForestRegressor (150 trees, depth 12)
- **Features**: year, month, quarter, day_of_week, week_of_year, unit_price, units_sold, promotion, holiday, discount, region, category, store (label-encoded)
- **Split**: Chronological 80/20 (no shuffle — time-series best practice)
- **Metrics**: MAE, RMSE, R²

---

## 📸 Pages

1. **Overview** — High-level KPIs and trend charts
2. **Forecasting** — Actual vs predicted with confidence bands
3. **Store Analysis** — Store-level performance deep dive
4. **Product Analysis** — Product and category insights
5. **AI Insights** — Auto-generated business recommendations + ML section

---

## 📝 License

MIT — free for portfolio & educational use.
