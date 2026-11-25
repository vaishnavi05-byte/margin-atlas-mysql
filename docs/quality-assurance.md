# Quality assurance evidence

## Expanded eleven-page release - 26 November 2026

- Refreshed the expanded editable PBIP in a separate Power BI Desktop instance, preserving the pre-existing unsaved report window.
- Verified 60 measures, 16 business tables and four Desktop date definitions. The four new pages rendered with their financial detail tables, slicers, clustered charts/donut and trends.
- All 14 regression tests passed, including exact discount boundaries, duplicate/orphan item rejection, unrecognized units and the deliberate exclusion of shared order costs from item merchandise margin.
- Executed both independent pandas notebooks. Item sales and COGS reconcile to orders; all 60 product results are independently reviewed.
- Executed eight additional native DAX result sets: 519 numeric comparisons across totals, channels, discount bands, payment methods and products passed. Product/discount marketing blanks and status-filter intersections passed. Re-executed the six original native DAX result sets successfully.
- Executed four new SELECT-only MySQL diagnostics in the separate loopback QA server: 302 numeric comparisons passed. The temporary server was shut down afterward.
- Observed native Paid Search bar cross-filtering: 8,416 orders, INR 41,394,535 net sales, INR 1,281,448 media spend and INR 16,965,833.63 contribution after marketing. Clicking the selected bar again restored the full snapshot. Native page-tab navigation opened the additional page.
- Captured all eleven pages after the table-binding correction. All measures now appear in their detail tables. Authoring CLI validation reports zero errors and eight schema-reachability warnings; those warnings are not claimed as full schema coverage.
- Product results are merchandise economics before refunds, inventory recovery and shared order costs. No causal promotion effect, product net profit or customer acquisition cost is claimed.

Expanded evidence: `commerce-native-validation.json`, `commerce-native-results.json`, `commerce-mysql-validation.json`, `commerce-mysql-results.json`, `commerce-findings.json` and `dashboard-suite.md`.

## Original seven-page baseline

Checks performed 25 November 2026 on the included synthetic snapshot.

- All eight CSV source grains, key relationships, date/channel media coverage and 60,209-item/order accounting were validated before export.
- The complete SQL schema/data rebuild and decision workbench executed in an isolated local MySQL 26.7.0 test instance. It left the original project database unchanged. All financial totals and 25 sample-eligible segment rankings matched Python. The temporary server was shut down afterward.
- The independent pandas notebook executed and reconciled line/order accounting and the exposure partition without calling the production aggregator.
- Analytical regression tests exercise duplicate/orphan rejection, financial identities, maturity eligibility, non-netted exposure, Wilson edge cases and intervention costs applied to every mature order.
- The native PBIP opened in Power BI Desktop 2.160.1151.0 and refreshed successfully. Imported PBIX output is included.
- Read-only DAX checks executed against Desktop's actual semantic engine using Microsoft's official ADOMD client. Totals, all 30 segment exposures/ranks/Wilson intervals, scenario boundary cases, unsupported marketing attribution and the nine-point sensitivity curve matched Python.
- Desktop category filtering was observed: selecting Apparel produced 9,833 orders and blank marketing-dependent measures. Clear selections restored 30,000 orders. Native page navigation opened Scenario lab. Selecting 15% recovery updated modeled benefit to INR 1,849,166.60 (display rounded on cards).
- Native drillthrough from Apparel–East opened 1,945 orders and INR 441,330.13 exposure; the back action returned to the queue. With 15% avoidance and INR 10 intervention cost, the scenario displayed INR 1,586,156.60 net change (rounded on cards).
- All seven pages were captured from the native report for visual inspection. PBIR CLI validation found zero errors; unavailable current-version schema endpoints are reported as warnings rather than claimed as complete schema coverage.

`data/validation.json` fingerprints source files. `docs/native-validation.json` and `docs/mysql-validation.json` contain machine-readable reconciliation evidence. Screenshot images show actual Desktop rendering; they are not design mockups.

The final GitHub Actions verification completed successfully on both Ubuntu and Windows: [run 45653041355](https://github.com/vaishnavi05-byte/margin-atlas-mysql/actions/runs/45653041355). Each runner rebuilt the data, passed all nine regression tests, executed the independent pandas notebook, validated native source bindings and reconciled saved DAX results with Python. CI does not launch Power BI Desktop; the native engine execution and visual interaction checks above were performed locally.

The release workflow is registered on main and checked out project commit `ba8f682bee0b43ba72399d6a110deff001717bc3`. This release changes documentation, evidence and completion metadata while retaining the tested functional source. See `docs/github-actions-verification.json` and `docs/images/GitHub verification.jpg`.

Power BI service hosting is separate from the delivered native PBIX/PBIP report.
