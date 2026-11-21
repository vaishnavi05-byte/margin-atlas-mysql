from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
input_file = project_root / "data" / "raw" / "products.csv"

products = pd.read_csv(input_file, dtype={"product": "string"})

expected_columns = [
    "product_id",
    "category_id",
    "product",
    "list_price_paise",
    "unit_cost_paise",
]

if list(products.columns) != expected_columns:
    raise ValueError("The CSV columns do not match our expected layout.")

# IDs and monetary amounts must contain whole numbers.
numeric_columns = [
    "product_id",
    "category_id",
    "list_price_paise",
    "unit_cost_paise",
]

for column in numeric_columns:
    if not pd.api.types.is_integer_dtype(products[column]):
        raise ValueError(f"{column} must contain whole numbers.")

checks = {
    "Exactly 60 products": len(products) == 60,
    "No missing values": not products.isna().any().any(),
    "Unique product IDs": products["product_id"].is_unique,
    "Valid categories": products["category_id"].isin([1, 2, 3, 4, 5]).all(),
    "Nonempty product names": products["product"].str.strip().ne("").all(),
    "Positive list prices": products["list_price_paise"].gt(0).all(),
    "Positive unit costs": products["unit_cost_paise"].gt(0).all(),
}

for check_name, passed in checks.items():
    result = "PASS" if passed else "FAIL"
    print(f"{check_name}: {result}")

if not all(checks.values()):
    raise ValueError("Validation failed. Review the failed checks above.")

output_folder = project_root / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "products_clean.csv"
products.to_csv(output_file, index=False, encoding="utf-8")

print("Validated CSV saved to:", output_file)