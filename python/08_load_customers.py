from pathlib import Path
import getpass
import pandas as pd
import mysql.connector

project_root = Path(__file__).resolve().parents[1]
input_file = (
    project_root / "data" / "processed" / "customers_clean.csv"
)

customers = pd.read_csv(
    input_file,
    dtype={
        "region": "string",
        "city_tier": "string",
        "first_order_date": "string",
    },
)

if customers["first_order_date"].notna().any():
    raise ValueError(
        "This initial load expects first_order_date to be empty."
    )

records = [
    (
        int(row.customer_id),
        row.region,
        row.city_tier,
        int(row.acquisition_channel_id),
        None,
    )
    for row in customers.itertuples(index=False)
]

password = getpass.getpass("Enter your project MySQL password: ")

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

insert_sql = """
INSERT INTO dim_customer (
    customer_id,
    region,
    city_tier,
    acquisition_channel_id,
    first_order_date
)
VALUES (%s, %s, %s, %s, %s)
"""

try:
    cursor.execute("SELECT COUNT(*) FROM dim_customer;")
    existing_count = cursor.fetchone()[0]

    if existing_count != 0:
        raise ValueError(
            "dim_customer already contains data. Inspect before reloading."
        )

    cursor.executemany(insert_sql, records)

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(first_order_date IS NULL)
        FROM dim_customer;
    """)

    loaded_count, pending_dates = cursor.fetchone()

    if loaded_count != len(records):
        raise ValueError("The database count does not match the CSV.")

    if pending_dates != loaded_count:
        raise ValueError("The initial first-order dates must all be NULL.")

    connection.commit()

    print("Customers loaded successfully:", loaded_count)
    print("Customers awaiting first-order dates:", pending_dates)

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()