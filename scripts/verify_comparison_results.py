"""Check native disconnected-period measures against row-level order extracts."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data/powerbi/FactOrders.csv').open()))
actual=json.loads((ROOT/'docs/comparison-dax-results.json').read_text(encoding='utf-8-sig'));checks=0
def compare(a,selected,first='2026-08',second='2026-09'):
    global checks
    groups=[[r for r in selected if r['month']==m] for m in [first,second]]
    sales=[sum(int(r['net_sales_paise']) for r in g)/100 for g in groups]
    contrib=[sum(int(r['contribution_before_marketing_paise']) for r in g)/100 for g in groups]
    expected=dict(Baseline=sales[0],Comparison=sales[1],SalesChange=sales[1]-sales[0],Growth=(sales[1]-sales[0])/sales[0] if sales[0] else None,BaselineContribution=contrib[0],ComparisonContribution=contrib[1],ContributionChange=contrib[1]-contrib[0],BaselineOrders=len(groups[0]),ComparisonOrders=len(groups[1]))
    for k,v in expected.items():
        if '['+k+']' in a:assert math.isclose(a['['+k+']'],v,abs_tol=1e-6,rel_tol=1e-10),(k,a,v);checks+=1
compare(actual[0]['rows'][0],rows)
for a in actual[1]['rows']:compare(a,[r for r in rows if r['region']==a['DimCustomer[region]']])
compare(actual[2]['rows'][0],[r for r in rows if r['channel']=='Paid Search'],'2025-01','2026-01')
result={'result':'PASS','numeric_comparisons':checks,'contexts':['default Aug vs Sep 2026','six regions','Jan 2025 vs Jan 2026, Paid Search'],'periods':'disconnected single-select controls; date filters replaced, other dimensions retained'}
(ROOT/'docs/comparison-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
