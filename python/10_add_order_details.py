from pathlib import Path
from datetime import date, timedelta
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
snapshot_date = date(2026, 9, 30)

schedule = pd.read_csv(
    project_root / "data" / "raw" / "order_schedule.csv",
    parse_dates=["order_date"],
)

customers = pd.read_csv(
    project_root / "data" / "processed" / "customers_clean.csv",
    usecols=[
        "customer_id",
        "region",
        "city_tier",
        "acquisition_channel_id",
    ],
)

# Many orders may reference one customer profile.
orders = schedule.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

required_attributes = [
    "region",
    "city_tier",
    "acquisition_channel_id",
]

if orders[required_attributes].isna().any().any():
    raise ValueError("Some orders lack valid customer attributes.")

rng = random.Random(20261123)
rows = []

for row in orders.itertuples(index=False):
    order_date = row.order_date.date()

    category_id = rng.choices(
        [1, 2, 3, 4, 5],
        weights=[32, 22, 18, 16, 12],
    )[0]

    cod_probability = 0.48 if row.city_tier == "Tier 3" else 0.27
    payment_method = (
        "COD" if rng.random() < cod_probability else "Prepaid"
    )

    promised_days = 4 if row.city_tier == "Tier 1" else 6
    promised_date = order_date + timedelta(days=promised_days)

    # Fictional service issue for practising regional investigation.
    service_issue = (
        row.region == "East"
        and order_date >= date(2026, 5, 1)
    )

    late_probability = 0.26 if service_issue else 0.10

    if rng.random() < late_probability:
        planned_delivery = promised_date + timedelta(
            days=rng.randint(1, 7)
        )
    else:
        planned_delivery = promised_date - timedelta(
            days=rng.randint(0, 2)
        )

    if rng.random() < 0.035:
        status = "Cancelled"
    elif planned_delivery <= snapshot_date:
        status = "Delivered"
    else:
        status = "In transit"

    delivered_date = (
        planned_delivery.isoformat()
        if status == "Delivered"
        else None
    )

    rows.append({
        "order_id": row.order_id,
        "customer_id": int(row.customer_id),
        "order_date": order_date.isoformat(),
        "category_id": category_id,
        "channel_id": int(row.acquisition_channel_id),
        "payment_method": payment_method,
        "promised_date": promised_date.isoformat(),
        "delivered_date": delivered_date,
        "status": status,
    })

base_orders = pd.DataFrame(rows)

output_file = project_root / "data" / "raw" / "orders_base.csv"
base_orders.to_csv(output_file, index=False, encoding="utf-8")

print("Base orders:", len(base_orders))
print("Unique order IDs:", base_orders["order_id"].nunique())
print("Columns:", len(base_orders.columns))
print("\nOrder status counts:")
print(base_orders["status"].value_counts().to_string())
print("\nCSV saved to:", output_file)
