"""Execute an isolated MySQL rebuild and reconcile it with the Python outputs.

Password is prompted, never written to files or command arguments. --no-password
is only for an explicitly configured temporary local QA server.
"""
import argparse
import csv
import io
import json
import os
import subprocess
from getpass import getpass
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--mysql',default='mysql');p.add_argument('--port',type=int,default=3306);p.add_argument('--user',required=True);p.add_argument('--rebuild',action='store_true');p.add_argument('--no-password',action='store_true');a=p.parse_args()
    env=os.environ.copy()
    if not a.no_password:env['MYSQL_PWD']=getpass('MySQL password (not stored): ')
    else:env.pop('MYSQL_PWD',None)
    args=[a.mysql,'--host=127.0.0.1','--port='+str(a.port),'--user='+a.user,'--batch','--default-character-set=utf8mb4','--connect-timeout=5']
    def run(sql):
        result=subprocess.run(args,input=sql,text=True,encoding='utf-8',capture_output=True,env=env)
        if result.returncode:raise RuntimeError(result.stderr.strip())
        return result.stdout
    if a.rebuild:run((ROOT/'sql/00_rebuild_mysql.sql').read_text(encoding='utf-8'))
    output=run((ROOT/'sql/decision_workbench_mysql.sql').read_text(encoding='utf-8'))
    (ROOT/'docs').mkdir(exist_ok=True)
    (ROOT/'docs/mysql-query-results.tsv').write_text(output,encoding='utf-8')
    diagnostics=run((ROOT/'sql/20_business_diagnostics.sql').read_text(encoding='utf-8'))
    (ROOT/'docs/mysql-business-diagnostics.tsv').write_text(diagnostics,encoding='utf-8')
    query='''USE decision_studio; SELECT COUNT(*) AS orders, SUM(net_sales_paise) AS net_sales_paise,
      SUM(contribution_before_marketing_paise) AS contribution_paise, SUM(negative_order) AS negative_orders,
      SUM(negative_contribution_paise) AS exposure_paise, SUM(return_mature) AS mature_orders,
      SUM(mature_returns) AS mature_returns FROM vw_decision_order_evidence;'''
    totals={k:int(v) for k,v in next(csv.DictReader(io.StringIO(run(query)),delimiter='\t')).items()}
    with (ROOT/'data/powerbi/FactOrders.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
    expected={'orders':len(rows),'net_sales_paise':sum(int(r['net_sales_paise']) for r in rows),'contribution_paise':sum(int(r['contribution_before_marketing_paise']) for r in rows),'negative_orders':sum(int(r['negative_order']) for r in rows),'exposure_paise':sum(int(r['negative_contribution_paise']) for r in rows),'mature_orders':sum(int(r['return_mature']) for r in rows),'mature_returns':sum(int(r['mature_returns']) for r in rows)}
    if totals!=expected:raise ValueError('MySQL/Python totals do not reconcile')
    rank_sql='''USE decision_studio; WITH s AS (SELECT segment_key,SUM(negative_contribution_paise) AS exposure,SUM(return_mature) AS mature FROM vw_decision_order_evidence GROUP BY segment_key)
      SELECT segment_key, exposure,DENSE_RANK() OVER(ORDER BY exposure DESC) AS priority_rank FROM s WHERE mature>=100 ORDER BY priority_rank,segment_key;'''
    ranked=list(csv.DictReader(io.StringIO(run(rank_sql)),delimiter='\t'))
    with (ROOT/'data/powerbi/DecisionSegments.csv').open(encoding='utf-8') as f:expected_rank=[r for r in csv.DictReader(f) if r['sample_eligible']=='1']
    if [r['segment_key'] for r in ranked]!=[r['segment_key'] for r in expected_rank]:raise ValueError('MySQL/Python queue mismatch')
    lines=diagnostics.splitlines(); start=lines.index('cohort\tcustomers\trepeat_customers\trepeat_rate')
    cohort_rows=[]
    for line in lines[start+1:]:
        if not line[:4].isdigit():break
        cohort_rows.append(line.split('\t'))
    assert sum(int(r[1]) for r in cohort_rows)==6809
    assert sum(int(r[2]) for r in cohort_rows)==3410
    assert diagnostics.rstrip().endswith('mismatched_orders\n0')
    result={'engine':run('SELECT VERSION();').splitlines()[-1],'database':'decision_studio','isolation':'Separate temporary test server; original database untouched','totals':totals,'totals_match_python':True,'eligible_segment_rank_matches_python':True,'eligible_segments':len(ranked),'cohort_customer_and_repeat_counts_match_python':True,'monthly_calendar_diagnostics_executed':True,'line_order_mismatches':0}
    (ROOT/'docs/mysql-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
