from pathlib import Path
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
output_folder = project_root / "data" / "raw"
output_folder.mkdir(parents=True, exist_ok=True)

rng = random.Random(20261121)

regions = ["North", "South", "West", "East", "Central"]
city_tiers = ["Tier 1", "Tier 2", "Tier 3"]
channel_ids = [1, 2, 3, 4, 5]

rows = []

for customer_id in range(1, 8001):
    rows.append({
        "customer_id": customer_id,
        "region": rng.choice(regions),
        "city_tier": rng.choices(
            city_tiers, weights=[45, 35, 20]
        )[0],
        "acquisition_channel_id": rng.choices(
            channel_ids, weights=[25, 28, 27, 12, 8]
        )[0],
        "first_order_date": None,
    })

customers = pd.DataFrame(rows)

# Introduce missing regions in 30 customer profiles.
customers.loc[customers.index[:30], "region"] = pd.NA

# Add exact copies of the final 20 profiles.
duplicate_rows = customers.tail(20).copy()

raw_customers = pd.concat(
    [customers, duplicate_rows],
    ignore_index=True,
)

output_file = output_folder / "customers.csv"
raw_customers.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
)

print(raw_customers.head())
print("Raw rows:", len(raw_customers))
print("Unique customer IDs:", raw_customers["customer_id"].nunique())
print("Exact duplicate rows:", raw_customers.duplicated().sum())
print("Missing regions:", raw_customers["region"].isna().sum())
print("CSV saved to:", output_file)