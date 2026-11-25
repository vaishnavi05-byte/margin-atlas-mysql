"""Create a complete MySQL 8+ schema and portable INSERT script from audited CSVs.

No database connection or credentials required. Existing databases are untouched.
The generated script creates a new database and fails if it already exists.
"""
import csv
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from audit_source import audit

ORDER=['dim_channel','dim_category','dim_customer','dim_product','dim_date','fact_orders','fact_order_items','fact_marketing']
PK={'dim_channel':['channel_id'],'dim_category':['category_id'],'dim_customer':['customer_id'],'dim_product':['product_id'],'dim_date':['date'],'fact_orders':['order_id'],'fact_order_items':['line_id'],'fact_marketing':['date','channel_id']}
FK={'dim_customer':[('acquisition_channel_id','dim_channel','channel_id')], 'dim_product':[('category_id','dim_category','category_id')], 'fact_orders':[('customer_id','dim_customer','customer_id'),('category_id','dim_category','category_id'),('channel_id','dim_channel','channel_id'),('order_date','dim_date','date')], 'fact_order_items':[('order_id','fact_orders','order_id'),('product_id','dim_product','product_id')], 'fact_marketing':[('date','dim_date','date'),('channel_id','dim_channel','channel_id')]}
DATES={'date','order_date','promised_date','delivered_date','first_order_date'}
NUMBERS={'quantity','year','month_number','return_flag','late_flag','delivery_eligible','return_mature','new_customer'}

def prepare():
    source=ROOT/'data/source'; audit(source)
    statements=['-- Generated from audited synthetic source. MySQL 8+. No DROP/REPLACE of databases.',
      'CREATE DATABASE decision_studio CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;',
      'USE decision_studio;',"SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';"]
    for name in ORDER:
        with (source/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f); rows=list(reader); columns=reader.fieldnames
        def numeric(c): return c.endswith('_paise') or c in NUMBERS or (c.endswith('_id') and c not in ['order_id','line_id'])
        definitions=[]
        for c in columns:
            kind='DATE' if c in DATES else 'BIGINT' if numeric(c) else 'VARCHAR(100)'
            definitions.append(f'`{c}` {kind}'+(' NULL' if c in ['delivered_date','first_order_date'] else ' NOT NULL'))
            if c.endswith('_paise') and c not in ['net_sales_paise','net_product_cost_paise','contribution_before_marketing_paise']:
                definitions.append(f'CHECK (`{c}` >= 0)')
        definitions.append('PRIMARY KEY ('+','.join('`'+c+'`' for c in PK[name])+')')
        for col,target,ref in FK.get(name,[]): definitions.append(f'FOREIGN KEY (`{col}`) REFERENCES `{target}` (`{ref}`)')
        statements.append('CREATE TABLE `'+name+'` (\n  '+',\n  '.join(definitions)+'\n) ENGINE=InnoDB;')
        def value(c,v):
            if v=='': return 'NULL'
            if numeric(c): return str(int(v))
            return "'"+v.replace('\\','\\\\').replace("'","''")+"'"
        for i in range(0,len(rows),500):
            values=['('+','.join(value(c,r[c]) for c in columns)+')' for r in rows[i:i+500]]
            statements.append('INSERT INTO `'+name+'` ('+','.join('`'+c+'`' for c in columns)+') VALUES\n'+',\n'.join(values)+';')
    statements.append('CREATE SQL SECURITY INVOKER VIEW vw_order_economics AS SELECT * FROM fact_orders;')
    path=ROOT/'sql/00_rebuild_mysql.sql'; path.write_text('\n\n'.join(statements)+'\n',encoding='utf-8')
    print('Prepared',path.name,'with foreign keys and',sum(1 for s in statements if s.startswith('INSERT')),'batched inserts.')

if __name__=='__main__': prepare()
