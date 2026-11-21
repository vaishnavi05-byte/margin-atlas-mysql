from pathlib import Path
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]

orders = pd.read_csv(
    project_root / "data" / "raw" / "orders_base.csv",
    parse_dates=["order_date"],
)

products = pd.read_csv(
    project_root / "data" / "processed" / "products_clean.csv"
)

products_by_category = {
    int(category_id): group.to_dict("records")
    for category_id, group in products.groupby("category_id")
}

rng = random.Random(20261124)
promo_start = pd.Timestamp("2026-03-01")
rows = []

for order in orders.itertuples(index=False):
    available_products = products_by_category[
        int(order.category_id)
    ]

    selected_products = rng.sample(
        available_products,
        k=rng.randint(1, 3),
    )

    # Fictional promotion policy for the simulated business.
    high_promo = (
        order.channel_id == 3
        and order.order_date >= promo_start
    )

    discount_percent = rng.choice(
        [18, 25, 30] if high_promo else [0, 5, 10, 15]
    )

    for line_number, product in enumerate(selected_products, 1):
        quantity = rng.choices(
            [1, 2, 3],
            weights=[80, 17, 3],
        )[0]

        if order.status == "Delivered":
            gross_paise = (
                int(product["list_price_paise"]) * quantity
            )

            discount_paise = (
                gross_paise * discount_percent // 100
            )

            cogs_paise = (
                int(product["unit_cost_paise"]) * quantity
            )
        else:
            gross_paise = 0
            discount_paise = 0
            cogs_paise = 0

        rows.append({
            "line_id": f"{order.order_id}-{line_number:02d}",
            "order_id": order.order_id,
            "product_id": int(product["product_id"]),
            "quantity": quantity,
            "gross_paise": gross_paise,
            "discount_paise": discount_paise,
            "cogs_paise": cogs_paise,
        })

items = pd.DataFrame(rows)

output_file = project_root / "data" / "raw" / "order_items.csv"
items.to_csv(output_file, index=False, encoding="utf-8")

print("Order lines generated:", len(items))
print("Unique line IDs:", items["line_id"].nunique())
print("Orders covered:", items["order_id"].nunique())
print("Products represented:", items["product_id"].nunique())
print("CSV saved to:", output_file)