from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
input_file = project_root / "data" / "raw" / "customers.csv"

raw = pd.read_csv(
    input_file,
    dtype={
        "region": "string",
        "city_tier": "string",
        "first_order_date": "string",
    },
)

# Identify extra copies of completely identical rows.
duplicate_mask = raw.duplicated(keep="first")

duplicate_log = raw.loc[duplicate_mask].copy()
duplicate_log.insert(0, "source_row", duplicate_log.index + 2)
duplicate_log["reason"] = "exact_duplicate"

customers = raw.loc[~duplicate_mask].copy()

# Repeated IDs with different details need investigation.
if customers["customer_id"].duplicated().any():
    raise ValueError(
        "Conflicting records share a customer ID. Review before continuing."
    )

# Find missing or whitespace-only regions.
missing_region = (
    customers["region"].isna()
    | customers["region"].str.strip().eq("")
)

# Record the original values before repairing them.
repair_log = customers.loc[
    missing_region, ["customer_id", "region"]
].copy()

repair_log = repair_log.rename(
    columns={"region": "original_region"}
)

repair_log.insert(0, "source_row", repair_log.index + 2)
repair_log["original_region"] = (
    repair_log["original_region"].fillna("<missing>")
)
repair_log["new_region"] = "Unknown"
repair_log["reason"] = "missing_region"

customers.loc[missing_region, "region"] = "Unknown"

processed_folder = project_root / "data" / "processed"
audit_folder = project_root / "data" / "audit"

processed_folder.mkdir(parents=True, exist_ok=True)
audit_folder.mkdir(parents=True, exist_ok=True)

duplicate_log.to_csv(
    audit_folder / "customer_duplicates.csv", index=False
)

repair_log.to_csv(
    audit_folder / "customer_region_repairs.csv", index=False
)

customers.to_csv(
    processed_folder / "customers_prepared.csv", index=False
)

print("Raw rows:", len(raw))
print("Duplicate rows logged:", len(duplicate_log))
print("Missing regions repaired:", len(repair_log))
print("Prepared customer rows:", len(customers))