"""
generate_data.py
Run once to produce data/sales.csv with all required columns:
date, store_id, region, category, department, product, units_sold,
unit_price, revenue, profit, promotion, holiday, discount,
temperature, fuel_price, cpi, unemployment, forecast
"""
import pandas as pd
import numpy as np
import os


def generate_retail_data(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    start, end = "2022-01-01", "2024-12-31"
    all_dates = pd.date_range(start, end, freq="D")
    dates = rng.choice(all_dates, n_rows)

    stores    = [f"Store {i:02d}" for i in range(1, 21)]          # 20 stores
    regions   = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Food & Grocery", "Furniture", "Fashion", "Home & Living"]

    # Each category maps to several departments
    dept_map = {
        "Electronics":    ["Mobiles & Tablets", "Computers", "Audio & Video", "Cameras", "Accessories"],
        "Food & Grocery": ["Beverages", "Snacks & Confectionery", "Dairy & Eggs", "Fresh Produce", "Frozen Foods"],
        "Furniture":      ["Living Room", "Bedroom", "Office Furniture", "Kitchen & Dining", "Outdoor"],
        "Fashion":        ["Men's Wear", "Women's Wear", "Kids' Fashion", "Footwear", "Accessories"],
        "Home & Living":  ["Kitchen", "Bath & Bedding", "Decor", "Lighting", "Storage & Organisation"],
    }

    products = {
        "Electronics":    ["Laptop", "Smartphone", "Tablet", "Headphones", "Smartwatch", "Camera", "TV", "Speaker"],
        "Food & Grocery": ["Beverages", "Snacks", "Dairy", "Bakery", "Fruits", "Vegetables", "Frozen Foods"],
        "Furniture":      ["Sofa", "Bed Frame", "Dining Table", "Office Chair", "Wardrobe", "Bookshelf"],
        "Fashion":        ["Jeans", "T-Shirt", "Jacket", "Sneakers", "Dress", "Handbag", "Watch"],
        "Home & Living":  ["Cookware", "Bedding", "Curtains", "Lamp", "Carpet", "Wall Art", "Storage"],
    }

    price_ranges = {
        "Electronics":    (200,  1800),
        "Food & Grocery": (5,    80),
        "Furniture":      (80,   1200),
        "Fashion":        (20,   350),
        "Home & Living":  (15,   400),
    }

    margin_rates = {
        "Electronics":    (0.12, 0.22),
        "Food & Grocery": (0.08, 0.18),
        "Furniture":      (0.22, 0.38),
        "Fashion":        (0.28, 0.45),
        "Home & Living":  (0.20, 0.35),
    }

    # Each store has a fixed region
    store_region_map = {s: regions[i % len(regions)] for i, s in enumerate(stores)}

    store_ids  = rng.choice(stores, n_rows)
    cat_arr    = rng.choice(categories, n_rows)
    dept_arr   = np.array([rng.choice(dept_map[c]) for c in cat_arr])
    prod_arr   = np.array([rng.choice(products[c]) for c in cat_arr])
    region_arr = np.array([store_region_map[s] for s in store_ids])

    unit_price = np.array([
        round(rng.uniform(*price_ranges[c]), 2) for c in cat_arr
    ])

    # Seasonality
    month_arr = pd.DatetimeIndex(dates).month
    seasonal  = np.select(
        [np.isin(month_arr, [11, 12]), np.isin(month_arr, [6, 7, 8])],
        [1.40, 1.15],
        default=1.0,
    )

    # Promotion (25 % of rows)
    promotion = rng.choice([0, 1], n_rows, p=[0.75, 0.25]).astype(int)

    # Holiday flag — major Indian + global retail dates
    holiday_dates = {
        "10-02", "10-24", "11-01", "11-14", "12-25", "12-31", "01-01",
        "01-14", "01-26", "02-14", "03-25", "04-14", "05-01", "08-15",
        "09-05", "10-31", "11-26",
    }
    date_mmdd = pd.DatetimeIndex(dates).strftime("%m-%d")
    holiday   = np.where(np.isin(date_mmdd, list(holiday_dates)), 1, 0).astype(int)

    # Units sold
    base_units    = rng.poisson(lam=22, size=n_rows)
    promo_boost   = promotion * rng.integers(5, 18, n_rows)
    holiday_boost = holiday   * rng.integers(8, 25, n_rows)
    units_sold    = (base_units * seasonal + promo_boost + holiday_boost).astype(int).clip(min=1)

    revenue = (units_sold * unit_price).round(2)

    profit = np.array([
        round(rev * rng.uniform(*margin_rates[cat]), 2)
        for rev, cat in zip(revenue, cat_arr)
    ])

    discount = np.where(promotion == 1, rng.uniform(0.05, 0.25, n_rows).round(2), 0.0)

    # ── Economic indicators (realistic ranges) ──────────────────────────
    # Temperature: varies by season and region
    base_temp = np.select(
        [np.isin(month_arr, [12, 1, 2]),
         np.isin(month_arr, [3, 4, 5]),
         np.isin(month_arr, [6, 7, 8]),
         np.isin(month_arr, [9, 10, 11])],
        [15.0, 28.0, 35.0, 22.0],
        default=25.0,
    )
    temperature = (base_temp + rng.uniform(-5, 5, n_rows)).round(1)

    # Fuel price: slow drift over years with noise
    date_idx    = (pd.DatetimeIndex(dates) - pd.Timestamp("2022-01-01")).days.values
    fuel_price  = (3.00 + 0.0005 * date_idx + rng.uniform(-0.2, 0.2, n_rows)).round(3)

    # CPI: gradually rises from ~200 to ~240
    cpi         = (200 + 0.008 * date_idx + rng.uniform(-2, 2, n_rows)).round(2)

    # Unemployment: slight seasonal variation
    unemployment = (6.0 + rng.uniform(-2, 2, n_rows)).round(2)

    # Forecast (actual + noise — used as training reference target)
    noise    = rng.uniform(0.88, 1.12, n_rows)
    forecast = (revenue * noise).round(2)

    df = pd.DataFrame({
        "date":         pd.to_datetime(dates),
        "store_id":     store_ids,
        "region":       region_arr,
        "category":     cat_arr,
        "department":   dept_arr,
        "product":      prod_arr,
        "units_sold":   units_sold,
        "unit_price":   unit_price,
        "revenue":      revenue,
        "profit":       profit,
        "promotion":    promotion,
        "holiday":      holiday,
        "discount":     discount,
        "temperature":  temperature,
        "fuel_price":   fuel_price,
        "cpi":          cpi,
        "unemployment": unemployment,
        "forecast":     forecast,
    }).sort_values("date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_retail_data(n_rows=5000)
    df.to_csv("data/sales.csv", index=False)
    print(f"✅ Generated {len(df):,} rows → data/sales.csv")
    print(f"   Columns : {list(df.columns)}")
    print(df.head(3).to_string())
