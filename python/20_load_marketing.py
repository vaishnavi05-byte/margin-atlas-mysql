from pathlib import Path
from getpass import getpass
import pandas as pd
import mysql.connector

project_root = Path(__file__).resolve().parents[1]

marketing = pd.read_csv(
    project_root / "data" / "processed" / "marketing_clean.csv",
    parse_dates=["date"],
)

expected_columns = ["date", "channel_id", "spend_paise"]

if marketing.columns.tolist() != expected_columns:
    raise ValueError("Unexpected marketing columns.")

if marketing.empty:
    raise ValueError("The validated marketing file is empty.")

records = [
    (
        row.date.date(),
        int(row.channel_id),
        int(row.spend_paise),
    )
    for row in marketing.itertuples(index=False)
]

insert_sql = """
    INSERT INTO fact_marketing (
        `date`,
        channel_id,
        spend_paise
    )
    VALUES (%s, %s, %s);
"""

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

    cursor.execute("SELECT COUNT(*) FROM fact_marketing;")

    if cursor.fetchone()[0] != 0:
        raise ValueError(
            "fact_marketing already contains data. Load stopped."
        )

    print("Loading marketing spend...", flush=True)

    batch_size = 1000

    for start in range(0, len(records), batch_size):
        cursor.executemany(
            insert_sql,
            records[start:start + batch_size],
        )

    # Compare every database row with the validated input.
    cursor.execute(
        """
        SELECT
            `date`,
            channel_id,
            spend_paise
        FROM fact_marketing
        ORDER BY `date`, channel_id;
        """
    )

    loaded_records = cursor.fetchall()

    if loaded_records != sorted(records):
        raise ValueError(
            "Database marketing data does not match the CSV."
        )

    connection.commit()

    print("Marketing rows loaded successfully:", len(loaded_records))
    print("Dates covered:", len({row[0] for row in loaded_records}))
    print("Channels covered:", len({row[1] for row in loaded_records}))
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