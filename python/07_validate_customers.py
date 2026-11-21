from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
input_file = (
    project_root / "data" / "processed" / "customers_prepared.csv"
)

customers = pd.read_csv(
    input_file,
    dtype={
        "region": "string",
        "city_tier": "string",
        "first_order_date": "string",
    },
)

expected_columns = [
    "customer_id",
    "region",
    "city_tier",
    "acquisition_channel_id",
    "first_order_date",
]

if list(customers.columns) != expected_columns:
    raise ValueError("Customer columns do not match the expected layout.")

for column in ["customer_id", "acquisition_channel_id"]:
    if not pd.api.types.is_integer_dtype(customers[column]):
        raise ValueError(f"{column} must contain whole numbers.")

required_fields = [
    "customer_id",
    "region",
    "city_tier",
    "acquisition_channel_id",
]

valid_regions = [
    "North", "South", "West", "East", "Central", "Unknown"
]

checks = {
    "Exactly 8000 customers": len(customers) == 8000,
    "Unique customer IDs": customers["customer_id"].is_unique,
    "No missing required values": (
        not customers[required_fields].isna().any().any()
    ),
    "Positive customer IDs": customers["customer_id"].gt(0).all(),
    "Valid regions": customers["region"].isin(valid_regions).all(),
    "Valid city tiers": customers["city_tier"].isin(
        ["Tier 1", "Tier 2", "Tier 3"]
    ).all(),
    "Valid acquisition channels": customers[
        "acquisition_channel_id"
    ].isin([1, 2, 3, 4, 5]).all(),
    "First-order dates awaiting transactions": (
        customers["first_order_date"].isna().all()
    ),
}

for check_name, passed in checks.items():
    result = "PASS" if passed else "FAIL"
    print(f"{check_name}: {result}")

# Save the validation results, including any failed checks.
report = pd.DataFrame([
    {"check": name, "passed": bool(passed)}
    for name, passed in checks.items()
])

audit_folder = project_root / "data" / "audit"
audit_folder.mkdir(parents=True, exist_ok=True)

report.to_csv(
    audit_folder / "customer_validation.csv",
    index=False,
)

if not all(checks.values()):
    raise ValueError("Customer validation failed. Review the report.")

output_file = (
    project_root / "data" / "processed" / "customers_clean.csv"
)

customers.to_csv(output_file, index=False, encoding="utf-8")

print("Validated customer rows:", len(customers))
print("Validated CSV saved to:", output_file)