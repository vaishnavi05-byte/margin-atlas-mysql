> Current release: **12 pages / 73 measures** with a colour refresh and period comparison. [Latest guide](premium-dashboard-release.md). This catalog documents the four commerce pages introduced in the previous 11-page release.

# E-commerce dashboard suite

Expanded 26 November 2026. Eleven analytical pages in one native Power BI report, including a contextual order-evidence page. This is one portfolio project with multiple dashboards; it is not eleven independent projects or eleven hosted Power BI Service dashboards.

## The four new business questions

| Dashboard | Decision supported | Filters and interactions | Important limit |
|---|---|---|---|
| Channel economics | Compare original acquisition channels after observed media spend | Month/channel slicers, channel bar cross-filter, trend, financial detail table | Date/channel spend is not causal attribution, incremental ROAS or customer acquisition cost |
| Promotion diagnostics | Investigate discount-band contribution and mature returns | Month/category/channel/band slicers, clustered financial bars, return-rate columns and detail rows | Product, channel and time mix can explain differences; no promotion treatment effect is estimated |
| Payment and fulfilment | Inspect payment mix, cancellation outcomes and service costs | Month/region/payment/status slicers, payment-mix donut, three-component cost trend and status detail | Shipped and delivered denominators differ; status selections intersect measures through KEEPFILTERS |
| Product and baskets | Compare product-bearing sales, units and merchandise margin | Month/category/channel/product slicers, category chart, sales/margin trend and sortable 60-product table | Item sales are before refunds. Shared order costs and inventory recovery are not allocated |

The original seven pages remain: Business pulse, Leakage explorer, Delivery signals, Customer cohorts, Decision queue, Scenario lab and Order evidence. The navigation rail links the ten main pages; Order evidence is reached through native segment drillthrough.

## Why these additions belong together

The first release investigated negative-order contribution and intervention economics. The expanded suite adds four different commercial views without inventing additional data sources: acquisition-channel spend, discount policy, payment/fulfilment processes and item merchandise economics. A reviewer can move from executive performance to a commercial question, apply a filter and inspect detail records in the same report.

## Changes to the data model

1. The eight raw source files remain unchanged and retain their SHA-256 fingerprints.
2. Python adds exact `discount_band` and sort fields to the order reporting export. Zero recognized sales remains a separate population.
3. `FactItems` imports all 60,209 source lines, with recognized units, sales before refund and pre-refund merchandise margin. Its sales and COGS reconcile with the order source.
4. `DimProduct` imports 60 products. Single-direction relationships link Orders to Items and Product to Items. Product filters do not flow backward to fabricate order-level contribution.
5. Twenty-five additional measures bring the model to 60 measures and 16 business tables. Four Desktop date definitions bring the serialized table count to 20.
6. Marketing guards now also reject unsupported product and discount-band contexts. The channel dashboard restricts its controls to supported date/channel dimensions.

## Examples you can explain in an interview

- Full snapshot: 70,630 recognized units and 28,563 distinct delivered item-bearing orders. Their ratio is approximately 2.47 units per delivered item-bearing order.
- Item sales before refund are INR 161,059,805; item COGS are INR 79,771,088; merchandise margin before refunds/shared costs is INR 81,288,717. These amounts must not be presented as net product profit.
- The full-snapshot discount/gross ratio is approximately 9.75%. Use the ratio of total discount to total gross, not an unweighted average of order discount percentages.
- There are 28,919 shipped orders and 1,081 cancelled orders. Fulfilment cost uses the shipped denominator, while processing fees use the delivered denominator.
- Selecting Paid Search in the native channel bar filtered the detail table to 8,416 orders, INR 41,394,535 net sales, INR 1,281,448 media spend and INR 16,965,833.63 contribution after marketing. Clicking the selected bar again restored the full snapshot.

## Verification and reproducibility

- `python scripts/reproduce.py` validates sources, rebuilds exports and runs 14 regression tests. Ordinary data reproduction preserves report definitions.
- `python scripts/analyze_independently.py` executes both independent pandas notebooks.
- `sql/30_commerce_dashboards.sql` contains four SELECT-only diagnostics. Their isolated MySQL execution reconciled 302 numeric comparisons.
- `tests/commerce_checks.dax` was executed in the actual Desktop semantic engine. The new results reconcile through 519 numeric comparisons plus attribution/status-filter guards.
- `python scripts/verify_native_results.py` reconciles both core and commerce native evidence. In CI this checks the saved evidence; it does not rerun Desktop.
- `python scripts/expand_dashboard_suite.py` is an optional authoring helper. Use `--report-only` to rebuild visual definitions without changing model definitions. It is not required for a normal refresh.

## Resume wording

"Developed an 11-page Power BI suite with 60 DAX measures covering channel economics, promotions, payment and fulfilment, product baskets, delivery and retention."

Keep this under the single Margin Atlas Decision Studio project. The separate Olist Excel/SQL project remains a second project. Do not count pages as separate projects or describe this synthetic portfolio as client work.

## Learning-material version

The earlier 60-chapter lecture explains the original seven-page, 35-measure baseline. This document and the second executed notebook explain the four-page extension and the additional 25 measures. The original business definitions and investigation workflow remain relevant.
