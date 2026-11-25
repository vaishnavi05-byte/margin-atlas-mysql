# Margin Atlas Decision Studio

**End-to-end e-commerce profitability investigation with MySQL, Python and native Power BI.**

Revenue can grow while thousands of orders lose contribution. This project helps a manager choose a category-region problem to investigate, inspect the affected orders and test the economics required for an intervention to break even.

The included **synthetic** snapshot contains 30,000 orders, 60,209 line items and 8,000 customers, January 2025–September 2026. These are simulated observations, not a company's realized results or savings.

![Business pulse](docs/images/Business%20pulse.png)

## Explore the dashboard

Open **[powerbi/MarginAtlasDecisionStudio.pbix](powerbi/MarginAtlasDecisionStudio.pbix)** in a current Power BI Desktop release. Imported data is included, so the snapshot works immediately.

For editable, version-controlled source, run `python scripts/configure_data_path.py`, open **[powerbi/DecisionStudio.pbip](powerbi/DecisionStudio.pbip)** and select **Home → Refresh**. For a moved PBIX, change its `DataFolder` parameter in Transform data → Manage parameters before refreshing.

In Desktop, **Ctrl-click navigation/reset buttons**, or select a button and press **Ctrl+Enter**. In reading mode, use a normal click. Reset clears the current page's slicers; it does not remove a drillthrough filter or reset every page.

| Page | Purpose and interactions |
|---|---|
| Business pulse | Sales/contribution trends, metric selector, month/channel/category filters |
| Leakage explorer | Category-region matrix, cost components, segment evidence |
| Delivery signals | Mature outcome denominators and Wilson 95% return-rate intervals |
| Customer cohorts | Complete 90-day windows, cohort/region filters, weighted totals |
| Decision queue | Dynamic exposure ranking and minimum mature-sample control |
| Scenario lab | Relative cost avoidance, per-order intervention costs, sensitivity curve |
| Order evidence | Native segment drillthrough, order/status filters and back navigation |

Right-click a **segment_key** cell in the leakage or decision table, then choose **Drill through → Order evidence**. Monetary source columns on the evidence page are in **paise**.

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

Read [the executed notebook](notebooks/01_profitability_investigation.ipynb) and [machine-readable findings](docs/findings.json).

### MySQL

Use MySQL 8+ with permission to create a new database:

```powershell
python scripts/run_mysql_checks.py --mysql "PATH/TO/mysql.exe" --user YOUR_LOCAL_USER --rebuild
```

The password is prompted, never saved to source or command arguments. The rebuild creates **decision_studio** and fails if it exists; it does not overwrite an existing database. Alternatively, open `sql/00_rebuild_mysql.sql` in Workbench, followed by `sql/decision_workbench_mysql.sql` and `sql/20_business_diagnostics.sql`.

SQL includes primary/foreign keys, integer monetary types, views, CTEs, window ranking, a calendar spine, monthly change, complete-window cohorts and spend-preserving joins. [Executed reconciliation](docs/mysql-validation.json) matches Python totals and eligible segment rankings. [Query results](docs/mysql-query-results.tsv) are included.

### Power BI and verification

The model uses single-direction dimensions, a dedicated date table and a separate date/channel marketing fact. Disconnected controls select metrics, sample thresholds and scenario assumptions; a separate recovery axis preserves the full sensitivity curve.

Editable TMDL is under `powerbi/DecisionStudio.SemanticModel/definition`; PBIR pages/actions are under `powerbi/DecisionStudio.Report/definition`. These are the authoritative report sources. Normal reproduction preserves these native definitions and your report edits.

[Native DAX checks](tests/native_checks.dax) were executed against Desktop's semantic engine using Microsoft's ADOMD client. They reconcile totals, all 30 segment exposures/ranks/intervals, marketing blanks at unsupported grain, scenario boundaries and a nine-point sensitivity curve. [Verification evidence](docs/native-validation.json) includes source hashes. See [QA notes](docs/quality-assurance.md) for refresh, rendering and interaction checks.

## Metric contracts

- **Net sales:** gross minus discounts minus refunds.
- **Contribution:** net sales minus COGS after recovered inventory, fulfilment, fees and reverse logistics. Fixed overhead and taxes are excluded.
- **Negative-order exposure:** absolute contribution of negative orders only; positive orders do not offset it. It is not recoverable savings.
- **Mature return rate:** returns divided by delivered orders observed for at least 30 days as of 30 September 2026.
- **Priority:** exposure rank among segments meeting the selected mature-sample threshold. It is diagnostic, not causal uplift. CSV ranking is fixed; report ranking responds to filter context.
- **Marketing:** date/channel grain, retaining spend without orders. Unsupported category, region, customer and order attribution returns blank.
- **Repeat rate:** another placed-and-delivered order before 90 days after first delivered purchase. Only complete cohort months are included; totals use customer counts.
- **Scenario:** relative avoidance of positive refund minus inventory recovery plus reverse-logistics cost on mature returned orders. Intervention costs apply to all mature orders selected. Demand response and efficacy are not estimated.

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

Read [hiring research](docs/hiring-research.md) and the [interview walkthrough](docs/interview-walkthrough.md). Do not describe this simulation as client work or modeled improvements as delivered impact. GitHub Actions is configured; a remote run and hosted Power BI publication require authenticated accounts and are separate from local validation.
