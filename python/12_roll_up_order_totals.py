from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]

orders = pd.read_csv(
    project_root / "data" / "raw" / "orders_base.csv"
)

items = pd.read_csv(
    project_root / "data" / "raw" / "order_items.csv"
)

# Every order must appear once in the base orders file.
if not orders["order_id"].is_unique:
    raise ValueError("Duplicate order IDs found in base orders.")

# Both files must cover exactly the same orders.
if set(orders["order_id"]) != set(items["order_id"]):
    raise ValueError("Order IDs do not match between the two files.")

money_columns = [
    "gross_paise",
    "discount_paise",
    "cogs_paise",
]

# Combine all product lines belonging to each order.
order_totals = (
    items.groupby("order_id", as_index=False)[money_columns]
    .sum()
)

# Attach one totals row to each base order.
orders_with_totals = orders.merge(
    order_totals,
    on="order_id",
    how="left",
    validate="one_to_one",
)

if orders_with_totals[money_columns].isna().any().any():
    raise ValueError("Some orders are missing financial totals.")

# Confirm that aggregation preserved every monetary amount.
for column in money_columns:
    line_total = int(items[column].sum())
    order_total = int(orders_with_totals[column].sum())

    if line_total != order_total:
        raise ValueError(f"Totals do not reconcile for {column}.")

output_file = (
    project_root / "data" / "raw" / "orders_with_totals.csv"
)

orders_with_totals.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
)

print("Orders prepared:", len(orders_with_totals))
print("Unique order IDs:", orders_with_totals["order_id"].nunique())
print("Columns:", len(orders_with_totals.columns))
print("Line amounts match order totals: PASS")
print("CSV saved to:", output_file)