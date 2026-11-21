from pathlib import Path
import getpass
import pandas as pd
import mysql.connector

project_root = Path(__file__).resolve().parents[1]
input_file = (
    project_root / "data" / "processed" / "products_clean.csv"
)

products = pd.read_csv(input_file)

records = [
    (
        int(row.product_id),
        int(row.category_id),
        row.product,
        int(row.list_price_paise),
        int(row.unit_cost_paise),
    )
    for row in products.itertuples(index=False)
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
INSERT INTO dim_product (
    product_id,
    category_id,
    product,
    list_price_paise,
    unit_cost_paise
)
VALUES (%s, %s, %s, %s, %s)
"""

try:
    cursor.execute("SELECT COUNT(*) FROM dim_product;")
    existing_count = cursor.fetchone()[0]

    if existing_count != 0:
        raise ValueError(
            "dim_product already contains data. Inspect it before reloading."
        )

    cursor.executemany(insert_sql, records)

    cursor.execute("SELECT COUNT(*) FROM dim_product;")
    loaded_count = cursor.fetchone()[0]

    if loaded_count != len(records):
        raise ValueError("The database count does not match the CSV.")

    connection.commit()
    print("Products loaded successfully:", loaded_count)

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()