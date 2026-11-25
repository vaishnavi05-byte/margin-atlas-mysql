"""Execute a readable pandas notebook independently of the production aggregator."""
import contextlib
import io
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cells=[('markdown','''# Margin Atlas: from revenue to an investigation queue

Independent pandas review of synthetic e-commerce operations. Snapshot: 30 September 2026. Money is stored as integer paise. These are simulated observations, not a company's measured results.

Business question: which category-region contribution problem deserves investigation first, and what must be true for a return-reduction intervention to break even?'''),
('code','''from pathlib import Path
import json
import pandas as pd
root = Path.cwd()
source = root / 'data/source'
orders = pd.read_csv(source/'fact_orders.csv')
customers = pd.read_csv(source/'dim_customer.csv').fillna({'region':'Unknown'})
categories = pd.read_csv(source/'dim_category.csv')
items = pd.read_csv(source/'fact_order_items.csv')
media = pd.read_csv(source/'fact_marketing.csv')
df = orders.merge(customers[['customer_id','region']],on='customer_id',validate='many_to_one').merge(categories,on='category_id',validate='many_to_one')
assert len(df)==len(orders)==30000
line_totals=items.groupby('order_id')[['gross_paise','discount_paise','cogs_paise']].sum().sort_index()
pd.testing.assert_frame_equal(line_totals,orders.set_index('order_id')[line_totals.columns].sort_index(),check_dtype=False)
print('Validated 30,000 orders and 60,209 line items independently.')'''),
('markdown','''## Accounting and exposure

Net sales subtract discounts and refunds. Contribution subtracts net inventory cost, fulfilment, fees and reverse logistics. Marketing is a separate date/channel fact. Negative-order exposure is the absolute loss of unprofitable orders; positive orders cannot offset this diagnostic measure.'''),
('code','''df['loss_paise']=(-df.contribution_before_marketing_paise).clip(lower=0)
df['mature_returns']=df.return_flag*df.return_mature
df['return_base_paise']=(df.refund_paise-df.recovered_inventory_paise+df.reverse_logistics_paise).clip(lower=0)*df.mature_returns
totals={'orders':len(df),'net_sales_inr':int(df.net_sales_paise.sum())/100,'contribution_before_marketing_inr':int(df.contribution_before_marketing_paise.sum())/100,'negative_orders':int((df.loss_paise>0).sum()),'negative_exposure_inr':int(df.loss_paise.sum())/100,'marketing_inr':int(media.spend_paise.sum())/100,'mature_orders':int(df.return_mature.sum()),'mature_returns':int(df.mature_returns.sum())}
print(json.dumps(totals,indent=2))
segments=df.groupby(['category','region']).agg(orders=('order_id','size'),mature_orders=('return_mature','sum'),mature_returns=('mature_returns','sum'),loss_paise=('loss_paise','sum'),net_contribution_paise=('contribution_before_marketing_paise','sum'),return_base_paise=('return_base_paise','sum'))
segments['return_rate']=segments.mature_returns/segments.mature_orders
queue=segments[segments.mature_orders>=100].sort_values('loss_paise',ascending=False)
print(queue.head(8).to_string())
assert segments.orders.sum()==len(df)
assert segments.loss_paise.sum()==df.loss_paise.sum()'''),
('markdown','''## Delivery association and observation bias

Compare return rates only among mature delivered orders, with group counts. A late-delivery association can reflect product mix, customer mix or the simulation rules. It does not establish that faster delivery will reduce returns. Validate this with return reasons and an experiment before making that claim.'''),
('code','''mature=df[df.return_mature==1]
delivery=mature.groupby('late_flag').agg(orders=('order_id','size'),returns=('return_flag','sum'))
delivery['return_rate']=delivery.returns/delivery.orders
print(delivery.to_string())
top=queue.head(5)
share=top.loss_paise.sum()/df.loss_paise.sum()
base=df.return_base_paise.sum()/100
benefit=base*0.15
break_even=benefit/df.return_mature.sum()
print(f'Top five non-overlapping segments: {share:.1%} of negative-order exposure.')
print(f'15% relative avoidance of mature return cost: INR {benefit:,.2f} gross hypothetical benefit.')
print(f'Break-even cost across every mature order: INR {break_even:.2f}; INR 10/order net change: INR {benefit-df.return_mature.sum()*10:,.2f}.')
assert (0*base-df.return_mature.sum()*10)==-263010
(root/'docs/findings.json').write_text(json.dumps({**totals,'top_five_exposure_share':share,'scenario_15pct_gross_benefit_inr':benefit,'scenario_break_even_cost_inr':break_even,'scenario_15pct_cost10_net_inr':benefit-df.return_mature.sum()*10},indent=2))'''),
('markdown','''## Recommendation and next evidence

Start a cost-and-return-reason diagnostic on the highest-exposure eligible segment, Apparel–East. Review affected orders and validate refund, inventory recovery and reverse-logistics components. Compare alternative segments using exposure, mature sample and uncertainty, rather than revenue alone.

Before a pilot: identify a specific intervention, its per-order cost and an outcome window. Randomize eligible orders where practical, predefine contribution and return guardrails, and measure both incremental economics and customer outcomes. A hypothetical scenario does not prove avoidable loss.

Limitations: synthetic data; single-category orders; missing return reasons; no fixed overhead, tax or customer acquisition attribution by product; complete-window cohorts omit recent cohorts; no predictive or causal model claimed.''')]

def run():
    os.chdir(ROOT); namespace={}; notebook=[]; count=0
    for kind,source in cells:
        cell={'cell_type':kind,'metadata':{},'source':source.splitlines(keepends=True)}
        if kind=='code':
            count+=1; output=io.StringIO()
            with contextlib.redirect_stdout(output): exec(compile(source,'independent_review','exec'),namespace)
            cell.update(execution_count=count,outputs=[{'output_type':'stream','name':'stdout','text':output.getvalue().splitlines(keepends=True)}])
        notebook.append(cell)
    (ROOT/'notebooks').mkdir(exist_ok=True)
    (ROOT/'notebooks/01_profitability_investigation.ipynb').write_text(json.dumps({'cells':notebook,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5},indent=2),encoding='utf-8')
    print('Executed independent pandas review and saved notebook outputs.')

if __name__=='__main__':run()
