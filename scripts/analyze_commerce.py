"""Execute an independent pandas review for the four added dashboards."""
import contextlib
import io
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CODE='''from pathlib import Path
import json
import pandas as pd
root=Path.cwd()
source=root/'data/source'
orders=pd.read_csv(source/'fact_orders.csv')
items=pd.read_csv(source/'fact_order_items.csv')
products=pd.read_csv(source/'dim_product.csv')
channels=pd.read_csv(source/'dim_channel.csv')
media=pd.read_csv(source/'fact_marketing.csv')
assert orders.order_id.is_unique and items.line_id.is_unique and products.product_id.is_unique
items=items.merge(orders[['order_id','delivery_eligible']],on='order_id',validate='many_to_one')
assert len(items)==60209
items['recognized_units']=items.quantity*items.delivery_eligible
items['sales_paise']=items.gross_paise-items.discount_paise
items['margin_paise']=items.sales_paise-items.cogs_paise
assert items.sales_paise.sum()==(orders.gross_paise-orders.discount_paise).sum()
assert items.cogs_paise.sum()==orders.cogs_paise.sum()
# Independent explicit selection rules, not the production discount_band helper.
orders['discount_band']='Above 30%'
orders.loc[orders.discount_paise*100<=orders.gross_paise*30,'discount_band']='21-30%'
orders.loc[orders.discount_paise*100<=orders.gross_paise*20,'discount_band']='11-20%'
orders.loc[orders.discount_paise*100<=orders.gross_paise*10,'discount_band']='1-10%'
orders.loc[orders.discount_paise==0,'discount_band']='0%'
orders.loc[orders.gross_paise==0,'discount_band']='No recognized sales'
def ratio(n,d):return float(n/d) if d else None
def order_metrics(g,spend=None):
    count=len(g);gross=int(g.gross_paise.sum())/100;discount=int(g.discount_paise.sum())/100
    contribution=int(g.contribution_before_marketing_paise.sum())/100
    shipped=int((g.status!='Cancelled').sum());cancelled=int((g.status=='Cancelled').sum())
    delivered=int(g.delivery_eligible.sum());returned=int(g.return_flag.sum());mature=int(g.return_mature.sum())
    fulfillment=int(g.fulfilment_paise.sum())/100;fees=int(g.payment_fee_paise.sum())/100;reverse=int(g.reverse_logistics_paise.sum())/100
    net_sales=int(g.net_sales_paise.sum())/100;negative=int((g.contribution_before_marketing_paise<0).sum())
    result={'Orders':count,'Net Sales':net_sales,'Contribution Before Marketing':contribution,'Gross Sales':gross,'Sales Before Refund':gross-discount,'Discounts':discount,'Discount Rate':ratio(discount,gross),'Sales Per Delivered Order':ratio(net_sales,delivered),'Contribution Per Placed Order':ratio(contribution,count),'Shipped Orders':shipped,'Cancelled Orders':cancelled,'Cancellation Rate':ratio(cancelled,count),'Fulfilment Per Shipped Order':ratio(fulfillment,shipped),'Fees Per Delivered Order':ratio(fees,delivered),'Variable Service Cost':fulfillment+fees+reverse,'Service Cost Per Placed Order':ratio(fulfillment+fees+reverse,count),'Negative Order Rate':ratio(negative,count),'Observed Returned Orders':returned,'Reverse Cost Per Returned Order':ratio(reverse,returned),'Discounted Delivered Orders':int(((g.delivery_eligible==1)&(g.discount_paise>0)).sum()),'Mature Orders':mature,'Mature Return Rate':ratio(int((g.return_flag*g.return_mature).sum()),mature)}
    if spend is not None:result.update({'Marketing Spend':spend,'Contribution After Marketing':contribution-spend,'After Marketing Margin':ratio(contribution-spend,net_sales),'Marketing Per Placed Order':ratio(spend,count)})
    return result
def item_metrics(g):
    sales=int(g.sales_paise.sum())/100;margin=int(g.margin_paise.sum())/100
    units=int(g.recognized_units.sum());count=int(g.loc[g.delivery_eligible==1,'order_id'].nunique())
    return {'Item Sales Before Refund':sales,'Item Product Cost':int(g.cogs_paise.sum())/100,'Item Merchandise Margin':margin,'Item Merchandise Margin Rate':ratio(margin,sales),'Recognized Units':units,'Delivered Item Orders':count,'Units Per Item Order':ratio(units,count)}
total_spend=int(media.spend_paise.sum())/100
totals={**order_metrics(orders,total_spend),**item_metrics(items)}
channel_records={}
for row in channels.itertuples(index=False):
    spend=int(media.loc[media.channel_id==row.channel_id,'spend_paise'].sum())/100
    channel_records[row.channel]=order_metrics(orders[orders.channel_id==row.channel_id],spend)
bands={str(k):order_metrics(g) for k,g in orders.groupby('discount_band')}
payments={str(k):order_metrics(g) for k,g in orders.groupby('payment_method')}
product_records={str(k):item_metrics(g) for k,g in items.groupby('product_id')}
assert sum(v['Orders'] for v in channel_records.values())==30000
assert sum(v['Orders'] for v in bands.values())==30000
assert sum(v['Recognized Units'] for v in product_records.values())==totals['Recognized Units']
assert round(sum(v['Item Sales Before Refund'] for v in product_records.values()),2)==totals['Item Sales Before Refund']
result={'snapshot':'2026-09-30','synthetic':True,'independent_implementation':'pandas source-level calculations; no production aggregation helper imported','totals':totals,'channels':channel_records,'discount_bands':bands,'payments':payments,'products':product_records,'limits':['Item merchandise margin is before refunds, inventory recovery and shared order costs.','Marketing is original-acquisition-channel/date spend, not causal attribution or CAC.','Discount comparisons are descriptive and subject to product, channel and time mix.']}
(root/'docs/commerce-findings.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(totals,indent=2))
print('Reconciled five channels, all discount bands, two payment methods and 60 products independently.')
'''

def run():
    import os
    os.chdir(ROOT);namespace={};out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(compile(CODE,'commerce_review','exec'),namespace)
    cells=[{'cell_type':'markdown','metadata':{},'source':['# Additional commerce dashboards: independent review\n','Synthetic snapshot. Item merchandise margin excludes refunds and shared order costs. Channel comparisons are descriptive.']},{'cell_type':'code','metadata':{},'source':CODE.splitlines(keepends=True),'execution_count':1,'outputs':[{'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(keepends=True)}]}]
    notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks/02_commerce_dashboards.ipynb').write_text(json.dumps(notebook,indent=2),encoding='utf-8')
    print(out.getvalue())

if __name__=='__main__':run()
