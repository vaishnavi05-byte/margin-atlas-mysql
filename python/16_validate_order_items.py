from pathlib import Path
import pandas as pd
from pandas.api.types import is_integer_dtype

project_root = Path(__file__).resolve().parents[1]

items = pd.read_csv(
    project_root / "data" / "raw" / "order_items.csv"
)

orders = pd.read_csv(
    project_root / "data" / "processed" / "orders_clean.csv"
)

products = pd.read_csv(
    project_root / "data" / "processed" / "products_clean.csv"
)

money_columns = [
    "gross_paise",
    "discount_paise",
    "cogs_paise",
]

expected_columns = [
    "line_id",
    "order_id",
    "product_id",
    "quantity",
] + money_columns

if items.columns.tolist() != expected_columns:
    raise ValueError("Unexpected order-item column layout.")

for column in ["product_id", "quantity"] + money_columns:
    if not is_integer_dtype(items[column]):
        raise ValueError(f"{column} must contain whole numbers.")

# Attach order details for checking each line.
order_lookup = orders[
    ["order_id", "category_id", "status"]
].rename(columns={"category_id": "order_category"})

joined = items.merge(
    order_lookup,
    on="order_id",
    how="left",
    validate="many_to_one",
)

# Attach product details for checking category, price, and cost.
product_lookup = products[
    [
        "product_id",
        "category_id",
        "list_price_paise",
        "unit_cost_paise",
    ]
].rename(columns={"category_id": "product_category"})

joined = joined.merge(
    product_lookup,
    on="product_id",
    how="left",
    validate="many_to_one",
)

delivered = joined["status"].eq("Delivered")

expected_gross = (
    joined["list_price_paise"] * joined["quantity"]
).where(delivered, 0)

expected_cogs = (
    joined["unit_cost_paise"] * joined["quantity"]
).where(delivered, 0)

# Sum lines separately for each order.
line_totals = (
    items.groupby("order_id", as_index=False)[money_columns]
    .sum()
)

comparison = orders[
    ["order_id"] + money_columns
].merge(
    line_totals,
    on="order_id",
    how="outer",
    suffixes=("_order", "_lines"),
    validate="one_to_one",
    indicator=True,
)

checks = {
    "No missing line values":
        items.notna().all().all(),

    "Unique line IDs":
        items["line_id"].is_unique,

    "Valid line ID format":
        items["line_id"].str.fullmatch(r"MA\d{7}-\d{2}").all(),

    "Line IDs match their parent orders":
        items["line_id"].str.rsplit("-", n=1).str[0].eq(
            items["order_id"]
        ).all(),

    "Every line references an existing order":
        items["order_id"].isin(orders["order_id"]).all(),

    "Every order has product lines":
        set(items["order_id"]) == set(orders["order_id"]),

    "Every line references an existing product":
        items["product_id"].isin(products["product_id"]).all(),

    "All catalog products represented":
        set(items["product_id"]) == set(products["product_id"]),

    "No repeated product within the same order":
        not items.duplicated(["order_id", "product_id"]).any(),

    "Positive quantities within database limits":
        items["quantity"].between(1, 65535).all(),

    "Product category matches order category":
        joined["product_category"].eq(
            joined["order_category"]
        ).all(),

    "Nonnegative line amounts":
        items[money_columns].ge(0).all().all(),

    "Line discounts do not exceed gross amounts":
        items["discount_paise"].le(items["gross_paise"]).all(),

    "Gross amounts match price times quantity":
        joined["gross_paise"].eq(expected_gross).all(),

    "Product costs match unit cost times quantity":
        joined["cogs_paise"].eq(expected_cogs).all(),

    "Order totals and line totals cover the same orders":
        comparison["_merge"].eq("both").all(),
}

for column in money_columns:
    checks[f"Every order reconciles: {column}"] = (
        comparison[f"{column}_order"].eq(
            comparison[f"{column}_lines"]
        ).all()
    )

audit_folder = project_root / "data" / "audit"
audit_folder.mkdir(parents=True, exist_ok=True)

pd.DataFrame(
    [
        {"check": name, "passed": bool(passed)}
        for name, passed in checks.items()
    ]
).to_csv(
    audit_folder / "order_item_validation.csv",
    index=False,
)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise ValueError("Order-item validation failed. Review FAIL results.")

output_file = (
    project_root / "data" / "processed" / "order_items_clean.csv"
)

items.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
)

print("\nValidated order lines:", len(items))
print("Orders covered:", items["order_id"].nunique())
print("Products represented:", items["product_id"].nunique())
print("Validated CSV saved to:", output_file)