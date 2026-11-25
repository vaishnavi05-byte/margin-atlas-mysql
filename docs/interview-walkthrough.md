# Interview walkthrough

## A five-minute demonstration

1. **Business problem (30 seconds):** A sales dashboard alone does not tell an operations manager which contribution issue to investigate. This project traces sales into variable contribution and ranks mutually exclusive category-region segments.
2. **Model and data quality (60 seconds):** Show the eight source tables and integer-paise accounting. Explain why items are aggregated before order joins and why marketing is a separate date/channel fact. Run the reproduction command or open the executed QA evidence.
3. **Investigation (60 seconds):** Use a category/month/channel slicer. Inspect negative-order exposure, then the decision queue. A positive net segment contribution can coexist with substantial loss-making orders. Explain why a low-sample segment has a blank rank.
4. **Evidence (45 seconds):** Drill through from a segment key to orders. Show refund, recovered inventory and reverse-logistics components. Monetary source columns are in paise; report measures divide by 100.
5. **Scenario (60 seconds):** Use 15% avoidance and INR 10 per mature order. Explain the cost denominator. Set avoidance to zero: the intervention still costs money. The full sensitivity curve uses a disconnected axis, so choosing a scenario point does not remove other points.
6. **Recommendation and limit (45 seconds):** Start a return-reason/cost diagnostic on Apparel–East; the top five eligible segments contain 44.97% of exposure. Request operational evidence and propose a controlled pilot. This synthetic analysis establishes no causal effect or realized savings.

## Questions to practise by writing the answer yourself

| Question | Explain and demonstrate |
|---|---|
| Why not join every table and sum sales? | One-to-many line joins duplicate order money; marketing is at another grain. Aggregate at a declared grain first. |
| Why paise? | Exact integer accounting across source, SQL and Python; convert to rupees at presentation boundaries. |
| How does the ranking respond to filters? | RANKX iterates selected segments and applies the minimum sample before ranking exposure. ALLSELECTED over the whole segment dimension removes row-level category/region restrictions while retaining the user's selection. |
| Why blank marketing for a category? | Date/channel spend cannot be causally or mechanically allocated to products with this dataset. Blank communicates an unsupported attribution. |
| Why 30-day maturity? | Recent deliveries have not had equal time to return. Excluding immature observations reduces this observation-window bias. The 30-day policy itself is an explicit assumption. |
| Why Wilson intervals? | A descriptive binomial interval behaves better than a naive symmetric approximation near zero/one and with small samples. It is not an intervention-effect confidence interval. |
| Why complete cohort months? | Recent cohorts have incomplete follow-up. Customer-count weighting avoids averaging rates with unequal denominators. |
| What does the scenario estimate? | A fixed-demand sensitivity calculation over observed mature return costs. It does not predict prevention efficacy, demand changes or savings. |
| How did you verify DAX? | Executed native queries and compared totals, all segment ranks/exposures/intervals and scenario boundaries against Python; also refreshed and inspected the native report. |
| How would this run in production? | Replace snapshot exports with governed sources; incremental ingestion, scheduled refresh, lineage, access control, monitoring and metric ownership would be separate deployment work. |

## A defensible experiment proposal

Choose one operational intervention after reviewing return reasons. Define eligibility, randomization unit and a fixed observation window. Predefine contribution per eligible order, mature return rate, delivery SLA and customer-experience guardrails. Estimate sample requirements from expected effect and variance; avoid claiming that this portfolio's sample is automatically sufficient. Track intervention costs for all eligible orders and compare outcomes by assigned treatment. Investigate contamination and missing outcomes before making a rollout decision.

## Resume wording you can substantiate

- Built an eight-table MySQL/Python workflow for 30,000 synthetic orders and 60,209 items; reconciled line/order finances and validated dashboard measures across SQL, Python and native DAX.
- Developed a seven-page Power BI report with dynamic segment ranking, mature return-rate intervals, complete 90-day cohorts, drillthrough and interactive intervention-cost scenarios.
- Identified 4,159 negative-contribution orders and prioritized non-overlapping investigation segments; separated INR 4.70 million of observed synthetic exposure from hypothetical recovery assumptions.

Use only features you can independently demonstrate and explain. Do not claim a percentage profit improvement, client engagement or deployed production pipeline from this simulation. Add the repository URL only after publication is verified.

## Practice tasks

Rebuild the exposure SQL from memory; reproduce one cohort denominator; explain CALCULATE versus row context; deliberately inject an orphan order or financial mismatch and observe the validation failure; show how a filter changes a rank; explain one limitation before an interviewer asks.
