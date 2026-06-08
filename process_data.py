import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "data" / "airbnb_listings.csv"
OUTPUT_JSON = ROOT / "data" / "airbnb_data.json"

# Load and clean
df = pd.read_csv(INPUT_CSV)
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df = df[(df["price"] > 0) & (df["price"] <= 1000)].copy()
df["neighbourhood_group"] = df["neighbourhood_group"].fillna("Unknown")
df["room_type"] = df["room_type"].fillna("Unknown")
df["neighbourhood"] = df["neighbourhood"].fillna("Unknown")

# --- Global KPIs ---
kpis = {
    "total_listings": int(len(df)),
    "avg_price": round(df["price"].mean(), 1),
    "total_hosts": int(df["host_id"].nunique()),
    "avg_reviews": round(df["number_of_reviews"].mean(), 1),
}

# --- By Borough ---
borough_grp = df.groupby("neighbourhood_group")
by_neighbourhood_group = (
    borough_grp.agg(listings=("price", "count"), avg_price=("price", "mean"))
    .round(1)
    .reset_index()
    .rename(columns={"neighbourhood_group": "name"})
    .sort_values("listings", ascending=False)
    .to_dict(orient="records")
)

# --- By Room Type ---
room_grp = df.groupby("room_type")
by_room_type = (
    room_grp.agg(count=("price", "count"), avg_price=("price", "mean"))
    .round(1)
    .reset_index()
    .rename(columns={"room_type": "type"})
    .sort_values("count", ascending=False)
    .to_dict(orient="records")
)

# --- Top 10 Neighbourhoods (global) ---
neigh_grp = df.groupby(["neighbourhood", "neighbourhood_group"])
top_neighbourhoods = (
    neigh_grp.agg(listings=("price", "count"), avg_price=("price", "mean"))
    .round(1)
    .reset_index()
    .rename(columns={"neighbourhood": "name", "neighbourhood_group": "borough"})
    .sort_values("listings", ascending=False)
    .head(10)
    .to_dict(orient="records")
)

# --- Price Distribution ---
bins = [0, 50, 100, 150, 200, 300, 1001]
labels = ["$0-50", "$51-100", "$101-150", "$151-200", "$201-300", "$301+"]
df["price_range"] = pd.cut(df["price"], bins=bins, labels=labels, right=True)
price_distribution = (
    df["price_range"]
    .value_counts()
    .reindex(labels, fill_value=0)
    .reset_index()
    .rename(columns={"price_range": "range", "count": "count"})
    .to_dict(orient="records")
)

# --- Availability by Borough ---
availability_by_borough = (
    borough_grp["availability_365"]
    .mean()
    .round(1)
    .reset_index()
    .rename(columns={"neighbourhood_group": "borough", "availability_365": "avg_availability"})
    .sort_values("avg_availability", ascending=False)
    .to_dict(orient="records")
)

# --- Per-borough breakdowns (for filter interactivity) ---
borough_breakdowns = {}
for borough, group in borough_grp:
    b_neigh = (
        group.groupby("neighbourhood")
        .agg(listings=("price", "count"), avg_price=("price", "mean"))
        .round(1)
        .reset_index()
        .rename(columns={"neighbourhood": "name"})
        .sort_values("listings", ascending=False)
        .head(10)
        .to_dict(orient="records")
    )
    borough_breakdowns[borough] = {
        "kpis": {
            "total_listings": int(len(group)),
            "avg_price": round(float(group["price"].mean()), 1),
            "total_hosts": int(group["host_id"].nunique()),
            "avg_reviews": round(float(group["number_of_reviews"].mean()), 1),
        },
        "top_neighbourhoods": b_neigh,
        "by_room_type": (
            group.groupby("room_type")
            .agg(count=("price", "count"), avg_price=("price", "mean"))
            .round(1)
            .reset_index()
            .rename(columns={"room_type": "type"})
            .sort_values("count", ascending=False)
            .to_dict(orient="records")
        ),
    }

result = {
    "meta": {
        "source": "Inside Airbnb",
        "city": "New York City",
        "snapshot": "2024",
        "notes": "Prices above $1000 excluded as outliers. All values pre-aggregated.",
    },
    "kpis": kpis,
    "by_neighbourhood_group": by_neighbourhood_group,
    "by_room_type": by_room_type,
    "top_neighbourhoods": top_neighbourhoods,
    "price_distribution": price_distribution,
    "availability_by_borough": availability_by_borough,
    "borough_breakdowns": borough_breakdowns,
}

OUTPUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"✅ Wrote {OUTPUT_JSON} — {len(df):,} listings processed")
