from pathlib import Path
import pandas as pd
from pandas.api.types import is_integer_dtype

project_root = Path(__file__).resolve().parents[1]
snapshot = pd.Timestamp("2026-09-30")

orders = pd.read_csv(
    project_root / "data" / "raw" / "orders_complete.csv"
)

customers = pd.read_csv(
    project_root / "data" / "processed" / "customers_clean.csv"
)

money_columns = [
    "gross_paise",
    "discount_paise",
    "refund_paise",
    "cogs_paise",
    "recovered_inventory_paise",
    "fulfilment_paise",
    "payment_fee_paise",
    "reverse_logistics_paise",
]

flag_columns = [
    "return_flag",
    "late_flag",
    "delivery_eligible",
    "return_mature",
    "new_customer",
]

expected_columns = [
    "order_id",
    "customer_id",
    "order_date",
    "category_id",
    "channel_id",
    "payment_method",
    "promised_date",
    "delivered_date",
    "status",
] + money_columns + flag_columns

if orders.columns.tolist() != expected_columns:
    raise ValueError("The order columns do not match the expected layout.")

integer_columns = [
    "customer_id", "category_id", "channel_id",
] + money_columns + flag_columns

for column in integer_columns:
    if not is_integer_dtype(orders[column]):
        raise ValueError(f"{column} must contain whole numbers.")

for column in ["order_date", "promised_date", "delivered_date"]:
    orders[column] = pd.to_datetime(
        orders[column],
        format="%Y-%m-%d",
        errors="raise",
    )

delivered = orders["status"].eq("Delivered")
returned = orders["return_flag"].eq(1)
cancelled = orders["status"].eq("Cancelled")

net_sale = orders["gross_paise"] - orders["discount_paise"]

expected_late = (
    delivered
    & orders["delivered_date"].gt(orders["promised_date"])
).astype(int)

expected_mature = (
    delivered
    & (
        orders["delivered_date"] + pd.Timedelta(days=30)
    ).le(snapshot)
).astype(int)

expected_new = pd.Series(0, index=orders.index)

first_indexes = (
    orders.loc[delivered]
    .sort_values(["customer_id", "order_date", "order_id"])
    .drop_duplicates("customer_id")
    .index
)

expected_new.loc[first_indexes] = 1

customer_channels = customers.set_index(
    "customer_id"
)["acquisition_channel_id"]

# Undelivered orders have no recognized sales or product costs.
zero_when_undelivered = [
    "gross_paise",
    "discount_paise",
    "refund_paise",
    "cogs_paise",
    "recovered_inventory_paise",
    "payment_fee_paise",
    "reverse_logistics_paise",
]

checks = {
    "Exactly 30,000 orders":
        len(orders) == 30000,

    "Unique order IDs":
        orders["order_id"].is_unique,

    "Valid order ID format":
        orders["order_id"].str.fullmatch(r"MA\d{7}").all(),

    "No missing required values":
        orders.drop(columns="delivered_date").notna().all().all(),

    "Existing customer IDs":
        orders["customer_id"].isin(customers["customer_id"]).all(),

    "Valid category IDs":
        orders["category_id"].isin([1, 2, 3, 4, 5]).all(),

    "Channel matches customer acquisition source":
        orders["channel_id"].eq(
            orders["customer_id"].map(customer_channels)
        ).all(),

    "Valid payment methods":
        orders["payment_method"].isin(["Prepaid", "COD"]).all(),

    "Valid order statuses":
        orders["status"].isin(
            ["Delivered", "In transit", "Cancelled"]
        ).all(),

    "Order dates within project period":
        orders["order_date"].between(
            pd.Timestamp("2025-01-01"), snapshot
        ).all(),

    "Promised dates on or after order dates":
        orders["promised_date"].ge(orders["order_date"]).all(),

    "Delivery dates present only for delivered orders":
        orders["delivered_date"].notna().eq(delivered).all(),

    "Delivery dates within valid range":
        (
            orders.loc[delivered, "delivered_date"].ge(
                orders.loc[delivered, "order_date"]
            )
            & orders.loc[delivered, "delivered_date"].le(snapshot)
        ).all(),

    "Nonnegative financial amounts":
        orders[money_columns].ge(0).all().all(),

    "Discounts do not exceed gross amounts":
        orders["discount_paise"].le(orders["gross_paise"]).all(),

    "Refunds match full returned sales":
        orders["refund_paise"].eq(
            net_sale.where(returned, 0)
        ).all(),

    "Inventory recovery does not exceed product cost":
        orders["recovered_inventory_paise"].le(
            orders["cogs_paise"]
        ).all(),

    "No return costs or recovery without a return":
        orders.loc[
            ~returned,
            ["reverse_logistics_paise", "recovered_inventory_paise"],
        ].eq(0).all().all(),

    "Undelivered orders have no recognized sales":
        orders.loc[
            ~delivered, zero_when_undelivered
        ].eq(0).all().all(),

    "Cancelled orders have no fulfilment cost":
        orders.loc[cancelled, "fulfilment_paise"].eq(0).all(),

    "All indicators are zero or one":
        orders[flag_columns].isin([0, 1]).all().all(),

    "Returns belong only to delivered orders":
        (~returned | delivered).all(),

    "Delivery indicators match statuses":
        orders["delivery_eligible"].eq(delivered.astype(int)).all(),

    "Late indicators match delivery dates":
        orders["late_flag"].eq(expected_late).all(),

    "Return maturity matches the 30-day window":
        orders["return_mature"].eq(expected_mature).all(),

    "First-purchase indicators match customer history":
        orders["new_customer"].eq(expected_new).all(),
}

audit_folder = project_root / "data" / "audit"
audit_folder.mkdir(parents=True, exist_ok=True)

pd.DataFrame(
    [
        {"check": name, "passed": bool(passed)}
        for name, passed in checks.items()
    ]
).to_csv(
    audit_folder / "order_validation.csv",
    index=False,
)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise ValueError("Order validation failed. Review the FAIL results.")

output_folder = project_root / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "orders_clean.csv"

orders.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
    date_format="%Y-%m-%d",
)

print("\nValidated orders:", len(orders))
print("Validated CSV saved to:", output_file)