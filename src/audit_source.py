"""Validate source grains and cross-table accounting before publishing outputs."""
import csv
from collections import defaultdict
from datetime import date, timedelta


def audit(source):
    def read(name):
        with (source/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:
            return list(csv.DictReader(f))
    tables={n:read(n) for n in ['dim_category','dim_channel','dim_customer','dim_product','dim_date','fact_orders','fact_order_items','fact_marketing']}
    def unique(name, keys):
        rows=tables[name]; seen=set()
        for r in rows:
            key=tuple(r[k] for k in keys)
            if key in seen: raise ValueError('Duplicate source grain: '+name)
            seen.add(key)
        return seen
    keys={n:{k[0] for k in unique(n,[col])} for n,col in [('dim_category','category_id'),('dim_channel','channel_id'),('dim_customer','customer_id'),('dim_product','product_id'),('dim_date','date'),('fact_orders','order_id'),('fact_order_items','line_id')]}
    def reference(rows,col,target):
        if any(r[col] not in keys[target] for r in rows): raise ValueError('Orphan '+col)
    reference(tables['dim_product'],'category_id','dim_category')
    reference(tables['dim_customer'],'acquisition_channel_id','dim_channel')
    reference(tables['fact_order_items'],'order_id','fact_orders')
    reference(tables['fact_order_items'],'product_id','dim_product')
    products={r['product_id']:r for r in tables['dim_product']}
    orders={r['order_id']:r for r in tables['fact_orders']}
    amounts=defaultdict(lambda:[0,0,0])
    for r in tables['fact_order_items']:
        if int(r['quantity'])<1: raise ValueError('Invalid item quantity')
        if products[r['product_id']]['category_id']!=orders[r['order_id']]['category_id']: raise ValueError('Item/order category mismatch')
        for j,col in enumerate(['gross_paise','discount_paise','cogs_paise']):
            value=int(r[col])
            if value<0: raise ValueError('Negative item amount')
            amounts[r['order_id']][j]+=value
    for r in orders.values():
        if amounts[r['order_id']]!=[int(r[c]) for c in ['gross_paise','discount_paise','cogs_paise']]: raise ValueError('Item/order reconciliation failed')
        if r['order_date'] not in keys['dim_date']: raise ValueError('Order outside date dimension')
    unique('fact_marketing',['date','channel_id'])
    reference(tables['fact_marketing'],'channel_id','dim_channel')
    if any(int(r['spend_paise'])<0 for r in tables['fact_marketing']): raise ValueError('Negative marketing spend')
    dates=sorted(keys['dim_date']); start=date.fromisoformat(dates[0]); end=date.fromisoformat(dates[-1])
    expected_dates={(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)}
    if set(dates)!=expected_dates: raise ValueError('Non-contiguous date dimension')
    expected={(d,c) for d in dates for c in keys['dim_channel']}
    observed={(r['date'],r['channel_id']) for r in tables['fact_marketing']}
    if expected!=observed: raise ValueError('Marketing date/channel coverage mismatch')
    return {'rows':{n:len(v) for n,v in tables.items()},'line_order_financial_reconciliation':True,'marketing_full_date_channel_coverage':True,'unique_grains_and_foreign_keys':True}
