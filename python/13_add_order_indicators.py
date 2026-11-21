from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
snapshot_date = pd.Timestamp("2026-09-30")

orders = pd.read_csv(
    project_root / "data" / "raw" / "orders_with_totals.csv",
    parse_dates=[
        "order_date",
        "promised_date",
        "delivered_date",
    ],
)

if not orders["order_id"].is_unique:
    raise ValueError("Duplicate order IDs found.")

delivered = orders["status"].eq("Delivered")

if orders.loc[delivered, "delivered_date"].isna().any():
    raise ValueError("A delivered order is missing its delivery date.")

if orders.loc[delivered, "delivered_date"].gt(snapshot_date).any():
    raise ValueError("A delivery date is after the snapshot date.")

# Delivered orders can be included in delivery performance metrics.
orders["delivery_eligible"] = delivered.astype(int)

# Only delivered orders can be classified as late.
orders["late_flag"] = (
    delivered
    & orders["delivered_date"].gt(orders["promised_date"])
).astype(int)

# Allow 30 days after delivery to observe returns.
orders["return_mature"] = (
    delivered
    & (
        orders["delivered_date"] + pd.Timedelta(days=30)
    ).le(snapshot_date)
).astype(int)

# Mark one first delivered purchase per customer.
# Use purchase date, with order ID breaking same-day ties.
orders["new_customer"] = 0

first_purchase_indexes = (
    orders.loc[delivered]
    .sort_values(["customer_id", "order_date", "order_id"])
    .drop_duplicates(subset="customer_id", keep="first")
    .index
)

orders.loc[first_purchase_indexes, "new_customer"] = 1

output_file = (
    project_root / "data" / "raw" / "orders_with_indicators.csv"
)

orders.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
    date_format="%Y-%m-%d",
)

print("Orders prepared:", len(orders))
print("Columns:", len(orders.columns))
print("Delivered orders:", int(orders["delivery_eligible"].sum()))
print("Late delivered orders:", int(orders["late_flag"].sum()))
print("Return-mature orders:", int(orders["return_mature"].sum()))
print("Customers with delivered purchases:", int(orders["new_customer"].sum()))
print("CSV saved to:", output_file)
