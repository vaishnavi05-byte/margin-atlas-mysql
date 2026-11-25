"""Reconcile actual Desktop DAX evidence with independent pandas findings."""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify():
    findings=json.loads((ROOT/'docs/commerce-findings.json').read_text())
    native=json.loads((ROOT/'docs/commerce-native-results.json').read_text(encoding='utf-8-sig'))
    checks=0
    def compare(row,expected,dimension=None):
        nonlocal checks
        for key,value in row.items():
            if key==dimension:continue
            name=key.strip('[]');want=expected[name]
            if want is None:assert value is None,(name,value,want)
            else:assert value is not None and math.isclose(value,want,rel_tol=1e-10,abs_tol=0.005),(name,value,want)
            checks+=1
    compare(native[0]['rows'][0],findings['totals'])
    for index,name,dimension in [(1,'channels','DimChannel[channel]'),(2,'discount_bands','FactOrders[discount_band]'),(3,'payments','FactOrders[payment_method]'),(4,'products','DimProduct[product_id]')]:
        assert len(native[index]['rows'])==len(findings[name]),name
        for row in native[index]['rows']:compare(row,findings[name][str(row[dimension])],dimension)
    row=native[5]['rows'][0]
    assert row['[Marketing Must Be Blank]'] is None and row['[After Marketing Must Be Blank]'] is None
    assert row['[Orders Stay At Order Grain]']==30000
    assert math.isclose(row['[Item Sales Before Refund]'],findings['products']['101']['Item Sales Before Refund'],abs_tol=.005)
    row=native[6]['rows'][0];assert all(v is None for v in row.values())
    row=native[7]['rows'][0]
    assert row['[Cancelled Orders]'] in (0,None) and row['[Cancellation Rate]'] in (0,None)
    assert row['[Shipped Orders]']>0 and row['[Fulfilment Per Shipped Order]']>0
    proof={'native_commerce_dax_matches_independent_pandas':True,'numeric_comparisons':checks,'channel_groups':len(findings['channels']),'discount_band_groups':len(findings['discount_bands']),'payment_groups':len(findings['payments']),'products':len(findings['products']),'product_and_discount_marketing_guards':True,'status_filter_intersection_verified':True,'source_sha256':json.loads((ROOT/'data/validation.json').read_text())['source_sha256']}
    (ROOT/'docs/commerce-native-validation.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(f'Additional dashboards: {checks} native numeric comparisons and filter guards passed.')

if __name__=='__main__':verify()
