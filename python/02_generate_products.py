from pathlib import Path
import random
import pandas as pd

# Locate the project folder.
project_root = Path(__file__).resolve().parents[1]

# Create the folder for generated source data.
output_folder = project_root / "data" / "raw"
output_folder.mkdir(parents=True, exist_ok=True)

# A fixed seed makes the generated data reproducible.
rng = random.Random(20261120)

categories = {
    1: "Apparel",
    2: "Beauty",
    3: "Home",
    4: "Electronics",
    5: "Wellness",
}

# Synthetic cost assumptions, expressed as percentages.
cost_percentages = {
    1: 40,
    2: 31,
    3: 47,
    4: 76,
    5: 35,
}

rows = []

for category_id, category in categories.items():
    for number in range(1, 13):
        price_paise = rng.randint(4, 45) * 10000
        cost_paise = (
            price_paise * cost_percentages[category_id] // 100
        )

        rows.append({
            "product_id": category_id * 100 + number,
            "category_id": category_id,
            "product": f"{category} {number:02d}",
            "list_price_paise": price_paise,
            "unit_cost_paise": cost_paise,
        })

products = pd.DataFrame(rows)

output_file = output_folder / "products.csv"
products.to_csv(output_file, index=False, encoding="utf-8")

print(products.head())
print("Products generated:", len(products))
print("CSV saved to:", output_file)