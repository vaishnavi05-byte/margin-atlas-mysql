from pathlib import Path
from getpass import getpass
import pandas as pd
import mysql.connector

project_root = Path(__file__).resolve().parents[1]

# Output name: (source query, expected number of rows)
exports = {
    "dim_channel": (
        "SELECT * FROM dim_channel ORDER BY channel_id;",
        5,
    ),
    "dim_category": (
        "SELECT * FROM dim_category ORDER BY category_id;",
        5,
    ),
    "dim_product": (
        "SELECT * FROM dim_product ORDER BY product_id;",
        60,
    ),
    "dim_customer": (
        "SELECT * FROM dim_customer ORDER BY customer_id;",
        8000,
    ),
    "dim_date": (
        "SELECT * FROM dim_date ORDER BY `date`;",
        638,
    ),
    "fact_orders": (
        "SELECT * FROM vw_order_economics ORDER BY order_id;",
        30000,
    ),
    "fact_order_items": (
        "SELECT * FROM fact_order_items ORDER BY line_id;",
        60209,
    ),
    "fact_marketing": (
        "SELECT * FROM fact_marketing ORDER BY `date`, channel_id;",
        3190,
    ),
}

password = getpass("Enter your project MySQL password: ")

connection = None
cursor = None
frames = {}

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

    # Read every table from one consistent database snapshot.
    connection.start_transaction(
        isolation_level="REPEATABLE READ",
        consistent_snapshot=True,
        readonly=True,
    )

    cursor = connection.cursor()

    for name, (query, expected_rows) in exports.items():
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]

        frame = pd.DataFrame.from_records(
            cursor.fetchall(),
            columns=columns,
        )

        if len(frame) != expected_rows:
            raise ValueError(
                f"{name}: expected {expected_rows} rows, "
                f"found {len(frame)}."
            )

        frames[name] = frame
        print(f"Read {name}: {len(frame)} rows", flush=True)

    connection.commit()

except Exception:
    if connection is not None:
        connection.rollback()
    raise

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None:
        connection.close()

# Write files only after all eight row-count checks pass.
output_folder = project_root / "data" / "powerbi"
output_folder.mkdir(parents=True, exist_ok=True)

for name, frame in frames.items():
    frame.to_csv(
        output_folder / f"{name}.csv",
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )

print("\nCSV files exported:", len(frames))
print("Power BI export folder:", output_folder)