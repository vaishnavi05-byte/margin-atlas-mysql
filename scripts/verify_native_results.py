"""Reconcile captured native DAX results against independent source-level totals."""
import csv
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    results=json.loads((ROOT/'docs/native-dax-results.json').read_text(encoding='utf-8-sig'))
    findings=json.loads((ROOT/'docs/findings.json').read_text())
    totals=results[0]['rows'][0]
    mapping={'[Orders]':'orders','[Net Sales]':'net_sales_inr','[Contribution]':'contribution_before_marketing_inr','[Negative Orders]':'negative_orders','[Exposure]':'negative_exposure_inr','[Mature Orders]':'mature_orders','[Mature Returns]':'mature_returns','[Marketing]':'marketing_inr'}
    for dax,key in mapping.items():
        if not math.isclose(totals[dax],findings[key],abs_tol=0.005):raise ValueError('Native mismatch: '+key)
    with (ROOT/'data/powerbi/DecisionSegments.csv').open() as f: segments={r['segment_key']:r for r in csv.DictReader(f)}
    for row in results[1]['rows']:
        s=segments[row['DimSegment[segment_key]']]
        assert math.isclose(row['[Exposure]'],int(s['negative_contribution_paise'])/100,abs_tol=.005)
        assert row['[Rank]']==(int(s['priority_rank']) if s['priority_rank'] else None)
        assert math.isclose(row['[Low95]'],float(s['return_rate_low95']),abs_tol=1e-10)
        assert math.isclose(row['[High95]'],float(s['return_rate_high95']),abs_tol=1e-10)
    assert results[2]['rows'][0]['[Net Change]']==-10*findings['mature_orders']
    assert results[3]['rows'][0]['[Marketing Must Be Blank]'] is None
    assert results[3]['rows'][0]['[After Marketing Must Be Blank]'] is None
    assert results[4]['rows'][0]['[Net Change]']==0
    if len(results)>5:
        curve=results[5]['rows'];assert len(curve)==9
        assert curve[0]['[Net]']==-10*findings['mature_orders']
        assert all(curve[i]['[Net]']<curve[i+1]['[Net]'] for i in range(8))
    manifest=json.loads((ROOT/'data/validation.json').read_text())
    verified={'native_dax_totals_match_independent_pandas':True,'all_30_segment_exposures_ranks_and_wilson_intervals_match_python':True,'scenario_boundary_and_marketing_grain_checks':True,'sensitivity_curve_verified':len(results)>5,'source_sha256':manifest['source_sha256']}
    (ROOT/'docs/native-validation.json').write_text(json.dumps(verified,indent=2),encoding='utf-8')
    print('Native DAX, ranking, Wilson intervals, scenario boundaries and attribution checks passed.')
if __name__=='__main__':
    verify()
    from verify_commerce_results import verify as verify_commerce
    verify_commerce()
    if (ROOT/'docs/comparison-dax-results.json').exists():
        import runpy
        runpy.run_path(str(ROOT/'scripts/verify_comparison_results.py'),run_name='__main__')
