from pathlib import Path
import pandas as pd
from pandas.api.types import is_integer_dtype

project_root = Path(__file__).resolve().parents[1]

marketing = pd.read_csv(
    project_root / "data" / "raw" / "marketing.csv"
)

expected_columns = ["date", "channel_id", "spend_paise"]

if marketing.columns.tolist() != expected_columns:
    raise ValueError("Unexpected marketing column layout.")

for column in ["channel_id", "spend_paise"]:
    if not is_integer_dtype(marketing[column]):
        raise ValueError(f"{column} must contain whole numbers.")

marketing["date"] = pd.to_datetime(
    marketing["date"],
    format="%Y-%m-%d",
    errors="raise",
)

expected_dates = pd.date_range(
    start="2025-01-01",
    end="2026-09-30",
    freq="D",
)

# Build the complete set of required date-channel combinations.
expected_pairs = pd.MultiIndex.from_product(
    [expected_dates, [1, 2, 3, 4, 5]],
    names=["date", "channel_id"],
)

actual_pairs = pd.MultiIndex.from_frame(
    marketing[["date", "channel_id"]]
)

checks = {
    "Exactly 3,190 marketing rows":
        len(marketing) == 3190,

    "No missing values":
        marketing.notna().all().all(),

    "Unique date-channel pairs":
        not marketing.duplicated(["date", "channel_id"]).any(),

    "Valid channel IDs":
        marketing["channel_id"].isin([1, 2, 3, 4, 5]).all(),

    "Dates within project period":
        marketing["date"].between(
            expected_dates.min(),
            expected_dates.max(),
        ).all(),

    "Every date has all five channels":
        expected_pairs.difference(actual_pairs).empty,

    "No unexpected date-channel pairs":
        actual_pairs.difference(expected_pairs).empty,

    "Nonnegative marketing spend":
        marketing["spend_paise"].ge(0).all(),

    "Organic has zero direct media spend":
        marketing.loc[
            marketing["channel_id"].eq(1),
            "spend_paise",
        ].eq(0).all(),
}

audit_folder = project_root / "data" / "audit"
audit_folder.mkdir(parents=True, exist_ok=True)

pd.DataFrame(
    [
        {"check": name, "passed": bool(passed)}
        for name, passed in checks.items()
    ]
).to_csv(
    audit_folder / "marketing_validation.csv",
    index=False,
)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise ValueError("Marketing validation failed. Review FAIL results.")

output_folder = project_root / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "marketing_clean.csv"

marketing.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
    date_format="%Y-%m-%d",
)

print("\nValidated marketing rows:", len(marketing))
print("Validated CSV saved to:", output_file)