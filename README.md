# Margin Atlas

An e-commerce analytics project investigating how discounts,
returns, fulfilment costs, and marketing affect contribution.

## Tools
MySQL, Python, Power BI, and GitHub.

## Data
Synthetic demonstration data generated with Python.

## Current progress
- Created and populated all eight MySQL tables.
- Generated, validated, and loaded 60 products and 8,000 customers.
- Logged 20 duplicate customer rows and repaired 30 missing regions.
- Loaded 30,000 orders and 60,209 product lines.
- Reconciled each order's gross amount, discount, and product cost.
- Updated customer first-purchase dates from delivered orders.
- Loaded 3,190 daily marketing records across five channels.
- Verified zero reconciliation issues in the final database checks.

## Simulation notes
- All data, budgets, costs, and business scenarios are synthetic.
- The reporting snapshot is 30 September 2026.
- Higher Paid Social promotions and East-region delivery delays
  were deliberately introduced for analytical practice.
  ## Power BI report
- Built an interactive Overview page in Margin Atlas.pbix.
- Added six KPI cards, a monthly trend, and a channel comparison.
- Added date-range and acquisition-channel slicers.
- Validated date and channel filters against source-data totals.
- Marketing spend is analyzed at date and acquisition-channel level.
## Promotions & Returns
- Added four KPIs, monthly discount and return trends, and a before/after comparison.
- Included only delivered orders with at least 30 days of follow-up.
- Validated Paid Social results against SQL: return rate rose from 10.78% to 16.89%, while contribution before marketing per mature order fell from INR 2,281.84 to INR 1,166.13.
- Documented the fixed snapshot, partial latest cohort, and limitations of causal interpretation.