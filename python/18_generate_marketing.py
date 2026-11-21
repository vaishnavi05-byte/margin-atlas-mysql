from pathlib import Path
import random
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
rng = random.Random(20261126)

dates = pd.date_range(
    start="2025-01-01",
    end="2026-09-30",
    freq="D",
)

# Fictional daily budget ranges in rupees.
daily_budget_ranges = {
    1: (0, 0),        # Organic: no direct media spend
    2: (1500, 2500),  # Paid Search
    3: (1800, 3000),  # Paid Social
    4: (200, 450),    # Email
    5: (250, 650),    # Affiliate
}

promo_start = pd.Timestamp("2026-03-01")
rows = []

for day in dates:
    for channel_id, budget_range in daily_budget_ranges.items():
        minimum, maximum = budget_range

        # Convert rupees to integer paise.
        spend_paise = rng.randint(minimum, maximum) * 100

        # Fictional increase in Paid Social budgets.
        if channel_id == 3 and day >= promo_start:
            spend_paise = spend_paise * 145 // 100

        rows.append({
            "date": day.strftime("%Y-%m-%d"),
            "channel_id": channel_id,
            "spend_paise": spend_paise,
        })

marketing = pd.DataFrame(rows)

output_folder = project_root / "data" / "raw"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "marketing.csv"

marketing.to_csv(
    output_file,
    index=False,
    encoding="utf-8",
)

print("Marketing rows generated:", len(marketing))
print("Unique dates:", marketing["date"].nunique())
print("Channels represented:", marketing["channel_id"].nunique())
print(
    "Duplicate date-channel pairs:",
    marketing.duplicated(["date", "channel_id"]).sum(),
)
print("Earliest date:", marketing["date"].min())
print("Latest date:", marketing["date"].max())
print("CSV saved to:", output_file)