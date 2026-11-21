from pathlib import Path
from getpass import getpass
import pandas as pd
import mysql.connector

project_root = Path(__file__).resolve().parents[1]

order_columns = [
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

item_columns = [
    "line_id",
    "order_id",
    "product_id",
    "quantity",
    "gross_paise",
    "discount_paise",
    "cogs_paise",
]

date_columns = {
    "order_date",
    "promised_date",
    "delivered_date",
}

text_columns = {
    "order_id",
    "payment_method",
    "status",
}

orders = pd.read_csv(
    project_root / "data" / "processed" / "orders_clean.csv",
    parse_dates=list(date_columns),
)

items = pd.read_csv(
    project_root / "data" / "processed" / "order_items_clean.csv"
)

if orders.columns.tolist() != order_columns:
    raise ValueError("Unexpected order columns.")

if items.columns.tolist() != item_columns:
    raise ValueError("Unexpected item columns.")

if orders.empty or items.empty:
    raise ValueError("The validated files must not be empty.")


def convert_order_value(column, value):
    if pd.isna(value):
        return None

    if column in date_columns:
        return value.date()

    if column in text_columns:
        return str(value)

    return int(value)


# Convert pandas values into native Python values for MySQL.
order_records = [
    tuple(
        convert_order_value(column, value)
        for column, value in zip(order_columns, row)
    )
    for row in orders.itertuples(index=False, name=None)
]

item_records = [
    (
        str(row.line_id),
        str(row.order_id),
        int(row.product_id),
        int(row.quantity),
        int(row.gross_paise),
        int(row.discount_paise),
        int(row.cogs_paise),
    )
    for row in items.itertuples(index=False)
]

order_sql = (
    "INSERT INTO fact_orders ("
    + ", ".join(f"`{column}`" for column in order_columns)
    + ") VALUES ("
    + ", ".join(["%s"] * len(order_columns))
    + ")"
)

item_sql = (
    "INSERT INTO fact_order_items ("
    + ", ".join(f"`{column}`" for column in item_columns)
    + ") VALUES ("
    + ", ".join(["%s"] * len(item_columns))
    + ")"
)


def insert_batches(cursor, sql, records):
    batch_size = 1000

    for start in range(0, len(records), batch_size):
        cursor.executemany(
            sql,
            records[start:start + batch_size],
        )


password = getpass("Enter your project MySQL password: ")

connection = None
cursor = None

try:
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="margin_atlas_app",
        password=password,
        database="margin_atlas",
        use_pure=True,
        connection_timeout=10,
        autocommit=False,
    )

    cursor = connection.cursor()

    # Stop if either table already contains data.
    for table in ["fact_orders", "fact_order_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`;")

        if cursor.fetchone()[0] != 0:
            raise ValueError(
                f"{table} already contains data. Load stopped."
            )

    print("Loading orders...", flush=True)
    insert_batches(cursor, order_sql, order_records)

    print("Loading product lines...", flush=True)
    insert_batches(cursor, item_sql, item_records)

    cursor.execute("SELECT COUNT(*) FROM fact_orders;")
    loaded_orders = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT order_id)
        FROM fact_order_items;
        """
    )
    loaded_items, covered_orders = cursor.fetchone()

    if loaded_orders != len(order_records):
        raise ValueError("Loaded order count does not match the CSV.")

    if loaded_items != len(item_records):
        raise ValueError("Loaded item count does not match the CSV.")

    if covered_orders != loaded_orders:
        raise ValueError("Some loaded orders have no product lines.")

    # Reconcile every order against its lines inside MySQL.
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fact_orders AS o
        LEFT JOIN (
            SELECT
                order_id,
                SUM(gross_paise) AS gross_paise,
                SUM(discount_paise) AS discount_paise,
                SUM(cogs_paise) AS cogs_paise
            FROM fact_order_items
            GROUP BY order_id
        ) AS i
            ON o.order_id = i.order_id
        WHERE i.order_id IS NULL
           OR o.gross_paise <> i.gross_paise
           OR o.discount_paise <> i.discount_paise
           OR o.cogs_paise <> i.cogs_paise;
        """
    )

    mismatches = cursor.fetchone()[0]

    if mismatches != 0:
        raise ValueError("Database order totals do not reconcile.")

    connection.commit()

    print("Orders loaded successfully:", loaded_orders)
    print("Product lines loaded successfully:", loaded_items)
    print("Orders covered by lines:", covered_orders)
    print("Database reconciliation: PASS")

except Exception:
    if connection is not None:
        connection.rollback()

    print("Load failed. Any uncommitted inserts were rolled back.")
    raise

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None:
        connection.close()