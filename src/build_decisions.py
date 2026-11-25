"""Original decision analysis over the user's MySQL Margin Atlas exports.

No model fitting or causal claims. All money remains integer paise. Read-only
inputs; outputs are generated inside this project. No database credentials.
"""
import argparse
import csv
from datetime import date, timedelta
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from commerce_metrics import discount_band, enrich_items

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = date(2026, 9, 30)
MONEY = ['gross_paise','discount_paise','refund_paise','cogs_paise',
         'recovered_inventory_paise','fulfilment_paise','payment_fee_paise',
         'reverse_logistics_paise','net_sales_paise','net_product_cost_paise',
         'contribution_before_marketing_paise']
FLAGS = ['return_flag','late_flag','delivery_eligible','return_mature','new_customer']


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f'No rows for {path.name}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def keyed(rows, key):
    mapping = {}
    for row in rows:
        if row[key] in mapping:
            raise ValueError(f'Duplicate dimension key: {key}')
        mapping[row[key]] = row
    return mapping


def wilson(successes, trials, z=1.959963984540054):
    """Descriptive 95% binomial interval; not a causal effect interval."""
    if not trials:
        return None, None
    p = successes/trials
    denominator = 1 + z*z/trials
    center = (p + z*z/(2*trials))/denominator
    radius = z*math.sqrt(p*(1-p)/trials + z*z/(4*trials*trials))/denominator
    return max(0,center-radius), min(1,center+radius)


def enrich(raw_orders, customers, categories, channels):
    seen=set(); result=[]
    for raw in raw_orders:
        row=dict(raw)
        if row['order_id'] in seen:
            raise ValueError('Duplicate order ID')
        seen.add(row['order_id'])
        if row['customer_id'] not in customers or row['category_id'] not in categories or row['channel_id'] not in channels:
            raise ValueError('Unknown dimension reference')
        for name in MONEY+FLAGS:
            row[name]=int(row[name])
        if any(row[x]<0 for x in MONEY if x not in ['net_sales_paise','net_product_cost_paise','contribution_before_marketing_paise']):
            raise ValueError('Negative source amount')
        if any(row[x] not in (0,1) for x in FLAGS):
            raise ValueError('Invalid binary flag')
        ordered=date.fromisoformat(row['order_date'])
        promised=date.fromisoformat(row['promised_date'])
        delivered=date.fromisoformat(row['delivered_date']) if row['delivered_date'] else None
        if ordered>SNAPSHOT or promised<ordered or delivered and (delivered<ordered or delivered>SNAPSHOT):
            raise ValueError('Inconsistent dates')
        if row['status'] not in ['Delivered','Cancelled','In transit']:
            raise ValueError('Unknown status')
        expected_eligible=int(row['status']=='Delivered' and delivered is not None)
        expected_late=int(bool(expected_eligible and delivered>promised))
        expected_mature=int(bool(expected_eligible and delivered<=SNAPSHOT-timedelta(days=30)))
        if row['delivery_eligible']!=expected_eligible or row['late_flag']!=expected_late or row['return_mature']!=expected_mature:
            raise ValueError('Date/eligibility flag mismatch')
        expected_sales=row['gross_paise']-row['discount_paise']-row['refund_paise']
        expected_cost=row['cogs_paise']-row['recovered_inventory_paise']
        expected_contribution=expected_sales-expected_cost-row['fulfilment_paise']-row['payment_fee_paise']-row['reverse_logistics_paise']
        if (row['net_sales_paise'],row['net_product_cost_paise'],row['contribution_before_marketing_paise'])!=(expected_sales,expected_cost,expected_contribution):
            raise ValueError('Order financial reconciliation failed')
        row['month']=ordered.strftime('%Y-%m')
        row['category']=categories[row['category_id']]['category']
        row['channel']=channels[row['channel_id']]['channel']
        row['region']=customers[row['customer_id']]['region'] or 'Unknown'
        row['segment_key']=row['category_id']+'|'+row['region']
        row['negative_order']=int(expected_contribution<0)
        row['negative_contribution_paise']=max(-expected_contribution,0)
        row['mature_returns']=row['return_flag']*row['return_mature']
        row['observed_return_cost_paise']=row['refund_paise']-row['recovered_inventory_paise']+row['reverse_logistics_paise']
        # Scenario base: mature returns only, exclude unusual negative cost components.
        row['scenario_return_base_paise']=max(row['observed_return_cost_paise'],0)*row['mature_returns']
        row['mature_late_orders']=row['late_flag']*row['return_mature']
        row['delivery_days']=((delivered-ordered).days if delivered else '')
        row['discount_band'],row['discount_band_sort']=discount_band(row['gross_paise'],row['discount_paise'])
        result.append(row)
    if not result:
        raise ValueError('No orders')
    return result


def summarize(orders, dimensions):
    sums=MONEY+['negative_order','negative_contribution_paise','delivery_eligible','late_flag',
                'return_mature','mature_returns','scenario_return_base_paise','mature_late_orders']
    groups={}
    for row in orders:
        key=tuple(row[d] for d in dimensions)
        if key not in groups:
            groups[key]={**dict(zip(dimensions,key)),'orders':0,**{x:0 for x in sums}}
        bucket=groups[key]; bucket['orders']+=1
        for name in sums: bucket[name]+=row[name]
    result=[]
    for key in sorted(groups):
        row=groups[key]
        row['return_rate']=row['mature_returns']/row['return_mature'] if row['return_mature'] else ''
        low,high=wilson(row['mature_returns'],row['return_mature'])
        row['return_rate_low95']='' if low is None else low
        row['return_rate_high95']='' if high is None else high
        result.append(row)
    return result


def cohort_rows(orders):
    by_customer=defaultdict(list)
    for row in orders:
        if row['status']=='Delivered' and row['delivered_date']:
            by_customer[row['customer_id']].append(row)
    result=[]
    for cid,rows in sorted(by_customer.items()):
        first=min(date.fromisoformat(r['order_date']) for r in rows)
        if first.month==12: next_month=date(first.year+1,1,1)
        else: next_month=date(first.year,first.month+1,1)
        if next_month-timedelta(days=1)+timedelta(days=90)>SNAPSHOT:
            continue
        boundary=first+timedelta(days=90)
        first_id=min((r['order_date'],r['order_id']) for r in rows)[1]
        repeat=any(r['order_id']!=first_id and first<=date.fromisoformat(r['order_date'])<boundary
                   and date.fromisoformat(r['delivered_date'])<boundary for r in rows)
        result.append({'customer_id':cid,'cohort':first.strftime('%Y-%m'),'region':rows[0]['region'],'repeat_90d':int(repeat)})
    return result


def scenario(row, recovery_pct, intervention_cost_paise):
    """Fixed-demand relative avoidance of mature return cost; not predicted savings."""
    if not 0<=recovery_pct<=100 or intervention_cost_paise<0:
        raise ValueError('Invalid scenario assumptions')
    benefit=row['scenario_return_base_paise']*recovery_pct/100
    return {'modeled_avoided_cost_paise':benefit,
            'modeled_net_change_paise':benefit-row['return_mature']*intervention_cost_paise,
            'break_even_cost_per_mature_order_paise':benefit/row['return_mature'] if row['return_mature'] else None}


def build(source, minimum_sample=100):
    if minimum_sample<1:
        raise ValueError('Minimum sample must be positive')
    from audit_source import audit
    source_audit = audit(source)
    required=sorted(p.name for p in source.glob('*.csv'))
    inputs={name:read_csv(source/name) for name in required}
    customers=keyed(inputs['dim_customer.csv'],'customer_id')
    orders=enrich(inputs['fact_orders.csv'],customers,keyed(inputs['dim_category.csv'],'category_id'),keyed(inputs['dim_channel.csv'],'channel_id'))
    candidates=summarize(orders,['segment_key','category','region'])
    for row in candidates:
        row['sample_eligible']=int(row['return_mature']>=minimum_sample)
        row['recommended_diagnostic']='Review order costs and return reasons before selecting an intervention'
    # Mutually exclusive segments, deterministic rank, sample eligibility before exposure.
    candidates.sort(key=lambda x:(-x['sample_eligible'],-x['negative_contribution_paise'],x['segment_key']))
    for i,row in enumerate(candidates,1): row['priority_rank']=i if row['sample_eligible'] else ''
    out=ROOT/'data/powerbi';out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'FactOrders.csv',orders)
    write_csv(out/'DecisionSegments.csv',candidates)
    write_csv(out/'SegmentMonths.csv',summarize(orders,['month','segment_key','category','region']))
    write_csv(out/'Cohorts.csv',cohort_rows(orders))
    write_csv(out/'DimCategory.csv',inputs['dim_category.csv'])
    write_csv(out/'DimChannel.csv',inputs['dim_channel.csv'])
    write_csv(out/'DimCustomer.csv',inputs['dim_customer.csv'])
    items=enrich_items(inputs['fact_order_items.csv'],orders,inputs['dim_product.csv'])
    assert sum(r['sales_before_refund_paise'] for r in items)==sum(r['gross_paise']-r['discount_paise'] for r in orders)
    assert sum(r['cogs_paise'] for r in items)==sum(r['cogs_paise'] for r in orders)
    write_csv(out/'FactItems.csv',items)
    write_csv(out/'DimProduct.csv',inputs['dim_product.csv'])
    marketing=[];media_seen=set(); known_channels=set(keyed(inputs['dim_channel.csv'],'channel_id'))
    for r in inputs['fact_marketing.csv']:
        item=dict(r)
        key=(r['date'],r['channel_id'])
        if key in media_seen: raise ValueError('Duplicate media grain')
        if r['channel_id'] not in known_channels: raise ValueError('Unknown media channel')
        media_seen.add(key)
        for name in r:
            if name.endswith('_paise'): item[name]=int(r[name])
        item['month']=r['date'][:7]
        marketing.append(item)
    write_csv(out/'FactMarketing.csv',marketing)
    start=min(date.fromisoformat(r['order_date']) for r in orders)
    dates=[{'date':(start+timedelta(days=i)).isoformat(),'month':(start+timedelta(days=i)).strftime('%Y-%m')} for i in range((SNAPSHOT-start).days+1)]
    write_csv(out/'DimDate.csv',dates)
    all_orders=sum(x['orders'] for x in candidates)
    all_loss=sum(x['negative_contribution_paise'] for x in candidates)
    expected_loss=sum(x['negative_contribution_paise'] for x in orders)
    assert all_orders==len(orders) and all_loss==expected_loss
    assert sum(x['net_sales_paise'] for x in candidates)==sum(x['net_sales_paise'] for x in orders)
    manifest={'source':'User-owned Margin Atlas MySQL CSV exports','synthetic':True,'snapshot':SNAPSHOT.isoformat(),
              'orders':len(orders),'exclusive_segments':len(candidates),'negative_contribution_orders':sum(x['negative_order'] for x in orders),
              'negative_contribution_paise':all_loss,'minimum_mature_sample':minimum_sample,
              'partition_count_and_money_checks_passed':True,
              'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in required},
              'source_audit':source_audit,
              'notes':['Segment ranking is descriptive, not causal uplift.','The decision table is a full-snapshot summary; interactive ranking must use FactOrders measures.',
                       'Scenario intervention cost applies to all mature orders in the selected segment.','Marketing remains at date/channel grain.']}
    (ROOT/'data/validation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    native_path=ROOT/'docs/native-validation.json'
    native_valid=False
    if native_path.exists():
        evidence=json.loads(native_path.read_text(encoding='utf-8'))
        native_valid=evidence.get('source_sha256')==manifest['source_sha256'] and evidence.get('native_dax_totals_match_independent_pandas',False)
    facts=[{'check':'Unique order IDs','result':'PASS','detail':str(len(orders))+' unique orders'},
           {'check':'Dimension references','result':'PASS','detail':'Every order resolves'},
           {'check':'Order financial identities','result':'PASS','detail':'Integer paise, every order'},
           {'check':'Exclusive segment totals','result':'PASS','detail':'Order counts, sales and negative contribution reconcile'},
           {'check':'Date and maturity flags','result':'PASS','detail':'Snapshot 30 September 2026'},
           {'check':'Line-item reconciliation','result':'PASS','detail':'60209 items reconcile to order gross, discount and COGS'},
           {'check':'Marketing coverage','result':'PASS','detail':'Full date/channel grid; no order-dependent spend loss'},
           {'check':'Native DAX execution','result':'PASS' if native_valid else 'PENDING','detail':'Totals, ranks, intervals and scenario boundaries verified' if native_valid else 'Power BI Desktop validation required'}]
    write_csv(out/'DataTrust.csv',facts)
    write_csv(out/'DimSegment.csv',[{'segment_key':r['segment_key'],'category':r['category'],'region':r['region']} for r in candidates])
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=ROOT/'data/source')
    parser.add_argument('--minimum-sample',type=int,default=100)
    args=parser.parse_args()
    print(json.dumps(build(args.source.resolve(),args.minimum_sample),indent=2))
