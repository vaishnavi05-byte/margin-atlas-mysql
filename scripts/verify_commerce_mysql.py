"""Execute SELECT-only commerce diagnostics against an already prepared QA DB."""
import argparse
import csv
import io
import json
import math
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify(mysql,port,user):
    sql=(ROOT/'sql/30_commerce_dashboards.sql').read_text(encoding='utf-8')
    statements=[s.strip() for s in '\n'.join(l for l in sql.splitlines() if not l.lstrip().startswith('--')).split(';') if s.strip()]
    assert statements[0]=='USE decision_studio' and len(statements)==5
    findings=json.loads((ROOT/'docs/commerce-findings.json').read_text())
    args=[mysql,'--no-defaults','--host=127.0.0.1','--port='+str(port),'--user='+user,'--batch','--default-character-set=utf8mb4']
    all_rows=[];checks=0
    def compare(actual,want):
        nonlocal checks
        assert math.isclose(float(actual),want,rel_tol=1e-7,abs_tol=.005),(actual,want)
        checks+=1
    for i,statement in enumerate(statements[1:]):
        result=subprocess.run(args,input='USE decision_studio;\n'+statement+';',text=True,encoding='utf-8',capture_output=True,check=True)
        rows=list(csv.DictReader(io.StringIO(result.stdout),delimiter='\t'));all_rows.append(rows)
        if i==0:
            assert len(rows)==5
            for r in rows:
                want=findings['channels'][r['channel']]
                for col,metric in [('placed_orders','Orders'),('net_sales_inr','Net Sales'),('spend_inr','Marketing Spend'),('after_marketing_inr','Contribution After Marketing')]:compare(r[col],want[metric])
        elif i==1:
            assert len(rows)==len(findings['discount_bands'])
            for r in rows:
                want=findings['discount_bands'][r['discount_band']]
                for col,metric in [('placed_orders','Orders'),('net_sales_inr','Net Sales'),('contribution_inr','Contribution Before Marketing'),('mature_orders','Mature Orders')]:compare(r[col],want[metric])
                if want['Mature Return Rate'] is None:assert r['mature_return_rate']=='NULL'
                else:compare(r['mature_return_rate'],want['Mature Return Rate'])
        elif i==2:
            with (ROOT/'data/source/fact_orders.csv').open() as f:source=list(csv.DictReader(f))
            assert len(rows)==6
            for r in rows:
                group=[s for s in source if s['payment_method']==r['payment_method'] and s['status']==r['status']]
                compare(r['placed_orders'],len(group))
                compare(r['service_cost_inr'],sum(sum(int(s[c]) for c in ['fulfilment_paise','payment_fee_paise','reverse_logistics_paise']) for s in group)/100)
                compare(r['contribution_inr'],sum(int(s['contribution_before_marketing_paise']) for s in group)/100)
        else:
            assert len(rows)==60
            for r in rows:
                want=findings['products'][r['product_id']]
                for col,metric in [('recognized_units','Recognized Units'),('delivered_item_orders','Delivered Item Orders'),('item_sales_before_refund_inr','Item Sales Before Refund'),('item_merchandise_margin_inr','Item Merchandise Margin')]:compare(r[col],want[metric])
    (ROOT/'docs/commerce-mysql-results.json').write_text(json.dumps(all_rows,indent=2),encoding='utf-8')
    proof={'executed_selects':4,'numeric_comparisons':checks,'all_commerce_sql_results_match_independent_source_review':True,'database':'decision_studio','isolation':'Temporary loopback QA server, port '+str(port)+'; original database unchanged'}
    (ROOT/'docs/commerce-mysql-validation.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mysql',required=True);p.add_argument('--port',type=int,default=3307);p.add_argument('--user',default='root');a=p.parse_args();verify(a.mysql,a.port,a.user)
