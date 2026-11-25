# Colour refresh and period comparison

The current suite has **12 native analytical pages and 73 DAX measures**. A midnight-blue workspace, turquoise and coral comparisons, rounded panels, compact financial cards and a numbered navigation rail replace the earlier visual theme. These original designs use the reference resume's breadth of business investigation without copying its layouts or claims.

## Compare periods

Two disconnected month controls let a reviewer compare any two available months. The opening selection is **August 2026 versus September 2026**. `CALCULATE` removes the date dimension context and `TREATAS` applies each selected month. Category, acquisition channel and selected region continue to constrain both sides consistently. Deltas are signed; growth divides the sales change by baseline sales. A blank/zero baseline does not produce an invented percentage.

Default full-snapshot comparison:

| Metric | August 2026 | September 2026 | Change |
|---|---:|---:|---:|
| Net sales, INR | 11,004,346 | 10,235,822 | −768,524 (−6.98%) |
| Contribution before marketing, INR | 4,490,904.45 | 4,482,675.83 | −8,228.62 |

The grouped region and category charts provide two-period context. Selecting a region cross-filters the cards and channel evidence. The comparison is descriptive; it does not establish why performance changed. The report uses synthetic observations and does not represent a company's realized results.

**40 numeric comparisons** reconcile actual native DAX results with the row-level order extract: full default values, six regions and a different pair of months filtered to Paid Search. See [queries](../tests/comparison_checks.dax), [results](comparison-dax-results.json) and [verification](comparison-validation.json).

## Interaction and display

In Desktop, Ctrl-click navigation/reset buttons and click charts normally. Slicers are page-specific; reset clears current-page slicers. Click a selected chart element again to clear its cross-filter. Monetary KPI cards use compact millions; chart axes and detail tables retain their own labelled units. Large negative amounts use parentheses. Evidence columns preserve paise where explicitly indicated.

The 11-page expanded PBIX and the seven-page baseline remain historical deliveries. **MarginAtlasDecisionStudio_Premium.pbix** is the current 12-page report. The existing Hinglish lecture covers the earlier seven-page/35-measure learning version; the four commerce pages and this comparison page are documented as later extensions.

## English interview answer

“I designed the report as an investigation workflow: start with the business pulse, identify contribution leakage, inspect mature delivery and retention outcomes, then drill into order evidence or test an explicit scenario. I added independent baseline and comparison month controls so users can compare periods while retaining channel, category and region context. The final suite has 12 analytical pages and 73 DAX measures. I checked the new period calculations against order-level data and kept hypothetical scenarios clearly separate from observed results.”
