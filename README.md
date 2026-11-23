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
## Delivery Performance
- Added date and region filters, four mature-order KPIs, a monthly trend, and a before/after comparison.
- Validated East-region results against SQL: late delivery rate rose from 9.86% to 24.29%, and return rate rose from 11.56% to 13.14%.
- Contribution before marketing per mature order fell from INR 2,186.42 to INR 1,998.35.
- Documented the observation window and limitations of causal interpretation.
## Customer Cohorts
- Analyzed 18 first-purchase cohorts from January 2025 through June 2026, requiring a complete 90-day observation window for each cohort.
- Counted customers with another order placed and delivered within 90 days of their first delivered purchase.
- Validated 6,809 eligible customers and 3,410 repeat customers: an overall repeat purchase rate of 50.08%, calculated from customer counts.
- Verified the June 2026 filter: 416 customers, 204 repeat customers, and a 49.04% repeat rate.