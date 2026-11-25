# Margin Atlas Decision Studio

**An 11-page e-commerce dashboard suite with MySQL, Python and native Power BI: 60 DAX measures, 30,000 synthetic orders and 60 products.**

[Published project branch](https://github.com/vaishnavi05-byte/margin-atlas-mysql/tree/codex/decision-studio) | [Interview walkthrough](docs/interview-walkthrough.md) | [Validation evidence](docs/quality-assurance.md)

**Verified on GitHub Actions:** [Windows and Linux checks passed](https://github.com/vaishnavi05-byte/margin-atlas-mysql/actions/runs/45716311301) for the expanded 11-page release. Both runners rebuilt the data, passed the 14-test suite, executed both notebooks and reconciled saved native evidence.

**Expanded-suite validation:** 14 regression tests pass locally. The added dashboards reconcile with independent pandas through **519 native DAX comparisons and 302 MySQL comparisons**. All eleven pages were refreshed and rendered in Power BI Desktop. GitHub Actions rebuilds the data, executes both notebooks, validates source bindings and reconciles saved native DAX evidence; it does not launch Desktop.

Revenue can grow while thousands of orders lose contribution. This project helps a manager choose a category-region problem to investigate, inspect the affected orders and test the economics required for an intervention to break even.

The included **synthetic** snapshot contains 30,000 orders, 60,209 line items and 8,000 customers, January 2025–September 2026. These are simulated observations, not a company's realized results or savings.

![Business pulse](docs/images/Business%20pulse.png)

## Explore the dashboard

Open **[the expanded native report](powerbi/MarginAtlasDecisionStudio_Expanded.pbix)** in a current Power BI Desktop release. Imported data is included, so the snapshot works immediately. The earlier `MarginAtlasDecisionStudio.pbix` is retained as the seven-page baseline; the expanded file is the current delivery.

For editable, version-controlled source, run `python scripts/configure_data_path.py`, open **[powerbi/DecisionStudio.pbip](powerbi/DecisionStudio.pbip)** and select **Home → Refresh**. For a moved PBIX, change its `DataFolder` parameter in Transform data → Manage parameters before refreshing.

In Desktop, **Ctrl-click navigation/reset buttons**. In reading mode, use a normal click. Reset clears the current page's slicers; it does not remove a chart selection, drillthrough filter or reset every page. Click a selected chart element again to clear its cross-filter.

| Page | Purpose and interactions |
|---|---|
| Business pulse | Sales/contribution trends, metric selector, month/channel/category filters |
| Leakage explorer | Category-region matrix, cost components, segment evidence |
| Delivery signals | Mature outcome denominators and Wilson 95% return-rate intervals |
| Customer cohorts | Complete 90-day windows, cohort/region filters, weighted totals |
| Decision queue | Dynamic exposure ranking and minimum mature-sample control |
| Scenario lab | Relative cost avoidance, per-order intervention costs, sensitivity curve |
| Channel economics | Acquisition-channel contribution after marketing, spend trends and per-order media cost |
| Promotion diagnostics | Exact discount bands, contribution comparisons, mature return rates and filters |
| Payment and fulfilment | COD/prepaid mix, shipped-order fulfilment cost, payment fees and cancellation outcomes |
| Product and baskets | Product sales and merchandise margin before refunds, recognized units and product-bearing baskets |
| Order evidence | Native segment drillthrough, order/status filters and back navigation |

Right-click a **segment_key** cell in the leakage or decision table, then choose **Drill through → Order evidence**. Monetary source columns on the evidence page are in **paise**.

### Four added dashboards

These are four distinct analytical pages in the same native report, not four unrelated projects or Power BI Service dashboards. Each has a different business question, native filters and a detail table. See [the dashboard catalog and interview explanation](docs/dashboard-suite.md).

**Channel economics — which acquisition channels leave contribution after observed media spend?**

![Channel economics](docs/images/Channel%20economics.png)

**Promotion diagnostics — how do discount bands differ in contribution and mature return outcomes?**

![Promotion diagnostics](docs/images/Promotion%20diagnostics.png)

**Payment and fulfilment — how do payment mix, shipping costs and order status affect economics?**

![Payment and fulfilment](docs/images/Payment%20and%20fulfilment.png)

**Product and baskets — which products generate merchandise sales, units and pre-refund margin?**

![Product and baskets](docs/images/Product%20and%20baskets.png)

## Findings

| Full-snapshot metric | Result |
|---|---:|
| Orders | 30,000 |
| Net sales | INR 142,622,893.00 |
| Contribution before marketing | INR 61,302,497.37 |
| Negative-contribution orders | 4,159 |
| Negative-order contribution exposure | INR 4,699,911.63 |
| Mature delivered orders / returned orders | 26,301 / 3,143 |
| Marketing spend | INR 3,534,460.75 |

The top five non-overlapping sample-eligible segments account for **44.97% of negative-order exposure**. Apparel–East has the highest exposure. Investigate cost components and return reasons before choosing an intervention.

At hypothetical 15% relative avoidance of mature return cost, gross modeled benefit is INR 1,849,166.60. Costing an intervention at INR 10 on **every mature order** gives modeled net change of INR 1,586,156.60 at unchanged demand. Break-even cost is INR 70.31 per mature order. These are sensitivity results, not achieved savings.

## Reproduce

Python 3.10+; production transformation and tests use the standard library:

```powershell
python scripts/reproduce.py
```

This validates all eight source tables, reconciles every order to its items, checks full date/channel marketing coverage, rebuilds decision exports, prepares the complete MySQL SQL file and runs regression checks. Native report definitions are preserved.

For the independent pandas investigation and executed notebook:

```powershell
python -m pip install -r requirements.txt
python scripts/analyze_independently.py
```

Read [the original investigation notebook](notebooks/01_profitability_investigation.ipynb), [the additional commerce notebook](notebooks/02_commerce_dashboards.ipynb), [core findings](docs/findings.json) and [expanded findings](docs/commerce-findings.json).

### MySQL

Use MySQL 8+ with permission to create a new database:

```powershell
python scripts/run_mysql_checks.py --mysql "PATH/TO/mysql.exe" --user YOUR_LOCAL_USER --rebuild
```

The password is prompted, never saved to source or command arguments. The rebuild creates **decision_studio** and fails if it exists; it does not overwrite an existing database. Alternatively, open `sql/00_rebuild_mysql.sql` in Workbench, followed by `sql/decision_workbench_mysql.sql` and `sql/20_business_diagnostics.sql`.

SQL includes primary/foreign keys, integer monetary types, views, CTEs, window ranking, a calendar spine, monthly change, complete-window cohorts and spend-preserving joins. [Core reconciliation](docs/mysql-validation.json) matches Python totals and eligible segment rankings. [Four additional diagnostic queries](sql/30_commerce_dashboards.sql) were executed against the isolated QA database and [302 numeric results reconciled](docs/commerce-mysql-validation.json). Their [query results](docs/commerce-mysql-results.json) are included. `scripts/verify_commerce_mysql.py` reruns those SELECT-only checks against an already prepared QA database.

### Power BI and verification

The model uses single-direction dimensions, a dedicated date table and a separate date/channel marketing fact. Orders filter the item fact through unique order IDs; a product dimension filters items without inventing product-level order costs. There are 16 business tables, plus four Desktop-generated date definitions. Disconnected controls select metrics, sample thresholds and scenario assumptions; a separate recovery axis preserves the full sensitivity curve.

Editable TMDL is under `powerbi/DecisionStudio.SemanticModel/definition`; PBIR pages/actions are under `powerbi/DecisionStudio.Report/definition`. These are the authoritative report sources. Normal reproduction preserves these native definitions and your report edits.

[Native DAX checks](tests/native_checks.dax) were executed against Desktop's semantic engine using Microsoft's ADOMD client. They reconcile totals, all 30 segment exposures/ranks/intervals, marketing blanks at unsupported grain, scenario boundaries and a nine-point sensitivity curve. [Verification evidence](docs/native-validation.json) includes source hashes. See [QA notes](docs/quality-assurance.md) for refresh, rendering and interaction checks.

[Additional native queries](tests/commerce_checks.dax) reconcile the 25 new measures, five channels, five observed discount bands, two payment methods and all 60 products. They also test product/discount marketing blanks and status-filter intersections. [519 numeric comparisons passed](docs/commerce-native-validation.json). The [current measure definitions](powerbi/measures.dax) contain all 60 formulas.

## Metric contracts

- **Net sales:** gross minus discounts minus refunds.
- **Contribution:** net sales minus COGS after recovered inventory, fulfilment, fees and reverse logistics. Fixed overhead and taxes are excluded.
- **Negative-order exposure:** absolute contribution of negative orders only; positive orders do not offset it. It is not recoverable savings.
- **Mature return rate:** returns divided by delivered orders observed for at least 30 days as of 30 September 2026.
- **Priority:** exposure rank among segments meeting the selected mature-sample threshold. It is diagnostic, not causal uplift. CSV ranking is fixed; report ranking responds to filter context.
- **Marketing:** date/channel grain, retaining spend without orders. Unsupported category, region, customer and order attribution returns blank.
- **Repeat rate:** another placed-and-delivered order before 90 days after the placement date of the first order with a delivered outcome. Only complete cohort months are included; totals use customer counts.
- **Scenario:** relative avoidance of positive refund minus inventory recovery plus reverse-logistics cost on mature returned orders. Intervention costs apply to all mature orders selected. Demand response and efficacy are not estimated.
- **Product merchandise economics:** item gross minus discount, before refunds; merchandise margin additionally subtracts item COGS. Inventory recovery, logistics, fees, marketing and other shared order costs are not allocated to products. This is not product contribution or net profit.
- **Recognized units:** quantity on delivered-outcome lines. Cancelled/in-transit line quantities are retained in the source but contribute zero recognized units.
- **Basket denominator:** `Delivered Item Orders` counts distinct delivered orders bearing the selected products. Totals are distinct counts, not sums of per-product order counts.
- **Discount band:** exact integer discount/gross boundaries. Zero gross is `No recognized sales`, distinct from a delivered zero-discount sale. Comparisons are descriptive, not causal promotion effects.
- **Fulfilment denominator:** shipped orders include Delivered and In transit; payment-fee denominator is delivered eligible orders. `KEEPFILTERS` preserves the selected order-status intersection.

## Files

| Folder | Contents |
|---|---|
| `data/source`, `data/powerbi` | Eight source tables and validated dashboard imports |
| `src`, `scripts`, `tests` | Production pipeline, reproduction and analytical QA |
| `sql`, `notebooks` | Complete SQL rebuild and executed independent review |
| `powerbi` | Native PBIX, editable PBIP/PBIR/TMDL and original theme |
| `docs` | Findings, screenshots, QA, research and interview walkthrough |
| `.github/workflows` | Reproduction and notebook checks for GitHub Actions |

## Originality and role alignment

This is an original extension of Vaishnavi's earlier Margin Atlas MySQL portfolio. Source SHA-256 fingerprints are in `data/validation.json`. No Aditya code, assets, wording, data or findings were copied; his public presentation informed the quality benchmark. Standard statistical and BI methods are not claimed as inventions.

Read [hiring research](docs/hiring-research.md) and the [interview walkthrough](docs/interview-walkthrough.md). Do not describe this simulation as client work or modeled improvements as delivered impact.

The [release verification workflow](https://github.com/vaishnavi05-byte/margin-atlas-mysql/actions/workflows/decision-studio.yml) is registered on the repository's main branch and checks out the selected project commit. To repeat it, choose **Run workflow**, keep the workflow branch as **main**, and enter `codex/decision-studio` or an exact project commit in **Project branch or commit to verify**. [Recorded CI evidence](docs/github-actions-verification.json) identifies the verified release. The delivered suite is a native PBIX/PBIP report; Power BI Service hosting is a separate deployment option.
