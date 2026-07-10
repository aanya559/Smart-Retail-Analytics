"""
train_model.py
Trains a RandomForestRegressor to predict revenue.
Expects data/sales.csv with columns produced by generate_data.py.
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURE_COLS = [
    "year", "month", "quarter", "day_of_week", "week_of_year",
    "units_sold", "promotion", "holiday",
    "temperature", "fuel_price", "cpi", "unemployment",
    "region_enc", "category_enc", "department_enc", "store_enc",
]


def build_features(df: pd.DataFrame):
    df = df.copy()
    df["date"]         = pd.to_datetime(df["date"])
    df["year"]         = df["date"].dt.year
    df["month"]        = df["date"].dt.month
    df["quarter"]      = df["date"].dt.quarter
    df["day_of_week"]  = df["date"].dt.dayofweek
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    le_region     = LabelEncoder()
    le_category   = LabelEncoder()
    le_department = LabelEncoder()
    le_store      = LabelEncoder()

    df["region_enc"]     = le_region.fit_transform(df["region"])
    df["category_enc"]   = le_category.fit_transform(df["category"])
    df["department_enc"] = le_department.fit_transform(df["department"].astype(str))
    df["store_enc"]      = le_store.fit_transform(df["store_id"].astype(str))

    encoders = {
        "region":     le_region,
        "category":   le_category,
        "department": le_department,
        "store":      le_store,
    }

    X = df[FEATURE_COLS]
    y = df["revenue"]
    return X, y, encoders


def train_and_save(
    data_path:  str = "data/sales.csv",
    model_path: str = "model/forecast.pkl",
):
    print("📂 Loading data...")
    df = pd.read_csv(data_path)
    df = df.sort_values("date").reset_index(drop=True)

    # Validate required columns
    required = ["date", "store_id", "region", "category", "department",
                "units_sold", "promotion", "holiday",
                "temperature", "fuel_price", "cpi", "unemployment", "revenue"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in data: {missing}. Run generate_data.py first.")

    X, y, encoders = build_features(df)

    # Chronological 80/20 split
    split   = int(len(X) * 0.80)
    X_train = X.iloc[:split];  X_test = X.iloc[split:]
    y_train = y.iloc[:split];  y_test = y.iloc[split:]

    print(f"🏋️  Training on {len(X_train):,} samples (test: {len(X_test):,})...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=14,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae   = mean_absolute_error(y_test, preds)
    rmse  = np.sqrt(mean_squared_error(y_test, preds))
    r2    = r2_score(y_test, preds)

    print(f"\n📊 Test Metrics")
    print(f"   MAE : ₹{mae:,.2f}")
    print(f"   RMSE: ₹{rmse:,.2f}")
    print(f"   R²  : {r2:.4f}")

    importance = pd.Series(
        model.feature_importances_, index=FEATURE_COLS
    ).sort_values(ascending=False)
    print("\n🔑 Top Feature Importances:")
    print(importance.head(8).to_string())

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    payload = {
        "model":              model,
        "feature_cols":       FEATURE_COLS,
        "encoders":           encoders,
        "metrics": {
            "MAE":  round(mae,  2),
            "RMSE": round(rmse, 2),
            "R2":   round(r2,   4),
        },
        "feature_importance": importance.to_dict(),
    }
    joblib.dump(payload, model_path)
    print(f"\n✅ Model saved → {model_path}")
    return payload


if __name__ == "__main__":
    train_and_save()
