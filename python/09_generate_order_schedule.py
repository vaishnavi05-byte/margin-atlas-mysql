from pathlib import Path
from datetime import date, timedelta
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]

customers = pd.read_csv(
    project_root / "data" / "processed" / "customers_clean.csv",
    usecols=["customer_id"],
)

customer_ids = customers["customer_id"].tolist()

if len(customer_ids) != 8000 or len(set(customer_ids)) != 8000:
    raise ValueError("Expected 8000 unique customer profiles.")

start_date = date(2025, 1, 1)
snapshot_date = date(2026, 9, 30)
target_orders = 30000

rng = random.Random(20261122)

date_span = (snapshot_date - start_date).days
first_placed_dates = {}
events = []

# Give every customer an initial placed order.
for customer_id in customer_ids:
    first_date = start_date + timedelta(
        days=rng.randint(0, date_span)
    )

    first_placed_dates[customer_id] = first_date

    events.append({
        "customer_id": customer_id,
        "order_date": first_date,
    })

# Customers with longer observation windows have more opportunities
# to place additional orders.
repeat_weights = [
    (snapshot_date - first_placed_dates[customer_id]).days
    for customer_id in customer_ids
]

repeat_customers = rng.choices(
    customer_ids,
    weights=repeat_weights,
    k=target_orders - len(events),
)

for customer_id in repeat_customers:
    first_date = first_placed_dates[customer_id]
    available_days = (snapshot_date - first_date).days

    repeat_date = first_date + timedelta(
        days=rng.randint(1, available_days)
    )

    events.append({
        "customer_id": customer_id,
        "order_date": repeat_date,
    })

events.sort(
    key=lambda row: (row["order_date"], row["customer_id"])
)

schedule = pd.DataFrame(events)

schedule.insert(
    0,
    "order_id",
    [f"MA{number:07d}" for number in range(1, len(schedule) + 1)],
)

output_folder = project_root / "data" / "raw"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "order_schedule.csv"
schedule.to_csv(output_file, index=False, encoding="utf-8")

print(schedule.head())
print("Scheduled orders:", len(schedule))
print("Unique order IDs:", schedule["order_id"].nunique())
print("Customer profiles represented:", schedule["customer_id"].nunique())
print("Earliest order date:", schedule["order_date"].min())
print("Latest order date:", schedule["order_date"].max())
print("CSV saved to:", output_file)