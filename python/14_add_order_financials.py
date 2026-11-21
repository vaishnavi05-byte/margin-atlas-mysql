from pathlib import Path
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
snapshot_date = pd.Timestamp("2026-09-30")
promo_start = pd.Timestamp("2026-03-01")
rng = random.Random(20261125)

orders = pd.read_csv(
    project_root / "data" / "raw" / "orders_with_indicators.csv",
    parse_dates=[
        "order_date",
        "promised_date",
        "delivered_date",
    ],
)

customers = pd.read_csv(
    project_root / "data" / "processed" / "customers_clean.csv",
    usecols=["customer_id", "city_tier"],
)

orders = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

if orders["city_tier"].isna().any():
    raise ValueError("Some orders have no matching customer city tier.")

# Fictional return probabilities by product category.
base_return_probability = {
    1: 0.17,  # Apparel
    2: 0.05,  # Beauty
    3: 0.07,  # Home
    4: 0.09,  # Electronics
    5: 0.04,  # Wellness
}

financial_rows = []

for order in orders.itertuples(index=False):
    delivered = order.delivery_eligible == 1

    refund_paise = 0
    recovered_inventory_paise = 0
    fulfilment_paise = 0
    payment_fee_paise = 0
    reverse_logistics_paise = 0
    return_flag = 0

    # Assume fulfilment costs arise when an order is shipped.
    if order.status != "Cancelled":
        fulfilment_paise = rng.randint(6500, 11500)

        if order.city_tier == "Tier 3":
            fulfilment_paise += 4500

    if delivered:
        net_sale_paise = (
            int(order.gross_paise) - int(order.discount_paise)
        )

        # Assume these processing fees are not refunded.
        fee_per_thousand = (
            23 if order.payment_method == "Prepaid" else 34
        )

        payment_fee_paise = (
            net_sale_paise * fee_per_thousand // 1000
        )

        return_probability = base_return_probability[
            int(order.category_id)
        ]

        if order.late_flag == 1:
            return_probability += 0.11

        high_promo = (
            order.channel_id == 3
            and order.order_date >= promo_start
        )

        if high_promo:
            return_probability += 0.06

        return_probability = min(return_probability, 0.50)

        if rng.random() < return_probability:
            simulated_return_date = (
                order.delivered_date
                + pd.Timedelta(days=rng.randint(2, 27))
            )

            # Recognize only returns observed by the snapshot.
            if simulated_return_date <= snapshot_date:
                return_flag = 1
                refund_paise = net_sale_paise
                reverse_logistics_paise = rng.randint(9000, 16000)

                # Assume 80% of returns allow inventory recovery.
                if rng.random() < 0.80:
                    recovered_inventory_paise = (
                        int(order.cogs_paise) * 82 // 100
                    )

    financial_rows.append({
        "refund_paise": refund_paise,
        "recovered_inventory_paise": recovered_inventory_paise,
        "fulfilment_paise": fulfilment_paise,
        "payment_fee_paise": payment_fee_paise,
        "reverse_logistics_paise": reverse_logistics_paise,
        "return_flag": return_flag,
    })

orders = pd.concat(
    [
        orders.drop(columns="city_tier"),
        pd.DataFrame(financial_rows),
    ],
    axis=1,
)

# Match the column order of our MySQL fact_orders table.
column_order = [
    "order_id",
    "customer_id",
    "order_date",
    "category_id",
    "channel_id",
    "payment_method",
    "promised_date",
    "delivered_date",
    "status",
    "gross_paise",
    "discount_paise",
    "refund_paise",
    "cogs_paise",
    "recovered_inventory_paise",
    "fulfilment_paise",
    "payment_fee_paise",
    "reverse_logistics_paise",
    "return_flag",
    "late_flag",
    "delivery_eligible",
    "return_mature",
    "new_customer",
]

orders = orders[column_order]

output_file = (
    project_root / "data" / "raw" / "orders_complete.csv"
)

orders.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
    date_format="%Y-%m-%d",
)

print("Orders prepared:", len(orders))
print("Unique order IDs:", orders["order_id"].nunique())
print("Columns:", len(orders.columns))
print("Observed returned orders:", int(orders["return_flag"].sum()))
print("CSV saved to:", output_file)