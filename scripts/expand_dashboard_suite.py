"""Idempotent native-source authoring for four additional commerce dashboards.

Run after data reproduction, before opening/reloading the PBIP in Desktop.
This is an authoring helper, not part of an ordinary refresh.
"""
import copy
import argparse
import hashlib
import json
import re
from pathlib import Path
import style_report
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'powerbi/DecisionStudio.SemanticModel/definition'
PAGES=ROOT/'powerbi/DecisionStudio.Report/definition/pages'
CURRENCY='"INR "#,0;("INR "#,0);"INR "0'
DECIMAL='0.00'; PERCENT='0.0%'
MEASURES={
 'Gross Sales':('DIVIDE(SUM(FactOrders[gross_paise]),100)',CURRENCY),
 'Sales Before Refund':('[Gross Sales]-[Discounts]',CURRENCY),
 'Discount Rate':('DIVIDE([Discounts],[Gross Sales])',PERCENT),
 'Sales Per Delivered Order':('DIVIDE([Net Sales],[Delivery Eligible Orders])',CURRENCY),
 'Contribution Per Placed Order':('DIVIDE([Contribution Before Marketing],[Orders])',CURRENCY),
 'After Marketing Margin':('DIVIDE([Contribution After Marketing],[Net Sales])',PERCENT),
 'Marketing Per Placed Order':('DIVIDE([Marketing Spend],[Orders])',CURRENCY),
 'Shipped Orders':('CALCULATE([Orders],KEEPFILTERS(FactOrders[status]<>"Cancelled"))','#,0'),
 'Cancelled Orders':('CALCULATE([Orders],KEEPFILTERS(FactOrders[status]="Cancelled"))','#,0'),
 'Cancellation Rate':('DIVIDE([Cancelled Orders],[Orders])',PERCENT),
 'Fulfilment Per Shipped Order':('DIVIDE([Fulfilment],[Shipped Orders])',CURRENCY),
 'Fees Per Delivered Order':('DIVIDE([Fees],[Delivery Eligible Orders])',CURRENCY),
 'Variable Service Cost':('[Fulfilment]+[Fees]+[Reverse Logistics]',CURRENCY),
 'Service Cost Per Placed Order':('DIVIDE([Variable Service Cost],[Orders])',CURRENCY),
 'Negative Order Rate':('DIVIDE([Negative Contribution Orders],[Orders])',PERCENT),
 'Observed Returned Orders':('SUM(FactOrders[return_flag])','#,0'),
 'Reverse Cost Per Returned Order':('DIVIDE([Reverse Logistics],[Observed Returned Orders])',CURRENCY),
 'Discounted Delivered Orders':('CALCULATE([Orders],KEEPFILTERS(FactOrders[delivery_eligible]=1),KEEPFILTERS(FactOrders[discount_paise]>0))','#,0'),
 'Item Sales Before Refund':('DIVIDE(SUM(FactItems[sales_before_refund_paise]),100)',CURRENCY),
 'Item Product Cost':('DIVIDE(SUM(FactItems[cogs_paise]),100)',CURRENCY),
 'Item Merchandise Margin':('DIVIDE(SUM(FactItems[merchandise_margin_paise]),100)',CURRENCY),
 'Item Merchandise Margin Rate':('DIVIDE([Item Merchandise Margin],[Item Sales Before Refund])',PERCENT),
 'Recognized Units':('SUM(FactItems[recognized_units])','#,0'),
 'Delivered Item Orders':('CALCULATE(DISTINCTCOUNT(FactItems[order_id]),KEEPFILTERS(FactOrders[delivery_eligible]=1))','#,0'),
 'Units Per Item Order':('DIVIDE([Recognized Units],[Delivered Item Orders])',DECIMAL),
}

def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2),encoding='utf-8')
def oid(value):return hashlib.sha256(('commerce-suite-'+value).encode()).hexdigest()[:20]
def field(table,name,measure=False):return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
def projection(table,name,measure=False):return {'field':field(table,name,measure),'queryRef':table+'.'+name,'nativeQueryRef':name,**({} if measure else {'active':True})}

def update_model():
    fact=MODEL/'tables/FactOrders.tmdl';text=fact.read_text(encoding='utf-8')
    for name,(expr,fmt) in MEASURES.items():
        block=f"\tmeasure '{name}' = {expr}\n\t\tformatString: {fmt}\n\n"
        pattern=r"\tmeasure '"+re.escape(name)+r"' = .*?(?=\n\t(?:measure|column|partition) |\Z)"
        if re.search(pattern,text,re.S):text=re.sub(pattern,lambda _:block.rstrip(),text,flags=re.S)
        else:text=text.replace('\tcolumn order_id',block+'\tcolumn order_id',1)
    for name,kind in [('discount_band','string'),('discount_band_sort','int64')]:
        if '\tcolumn '+name+'\n' not in text:
            extra='\n\t\tsortByColumn: discount_band_sort' if name=='discount_band' else ''
            text=text.replace('\tpartition FactOrders',f'\tcolumn {name}\n\t\tdataType: {kind}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {name}{extra}\n\n\tpartition FactOrders',1)
    text=text.replace('{"delivery_days",Int64.Type}})', '{"delivery_days",Int64.Type},{"discount_band",type text},{"discount_band_sort",Int64.Type}})')
    guard='ISFILTERED(DimCategory)||'
    if 'ISFILTERED(DimProduct)' not in text:
        text=text.replace(guard,'ISFILTERED(DimProduct)||ISFILTERED(FactItems[product_id])||ISFILTERED(FactItems[order_id])||ISFILTERED(FactOrders[discount_band])||'+guard)
    fact.write_text(text,encoding='utf-8')
    def table(name,columns):
        parts=['table '+name,'']
        for col,kind in columns:
            parts.extend([f'\tcolumn {col}',f'\t\tdataType: {kind}','\t\tsummarizeBy: '+('sum' if col.endswith('_paise') or col in ['quantity','recognized_units'] else 'none'),f'\t\tsourceColumn: {col}',''])
        types=','.join('{"'+col+'",'+('type text' if kind=='string' else 'Int64.Type')+'}' for col,kind in columns)
        parts.extend([f'\tpartition {name} = m','\t\tmode: import',f'\t\tsource = ReadCSV("{name}",{{{types}}})',''])
        (MODEL/'tables'/(name+'.tmdl')).write_text('\n'.join(parts),encoding='utf-8')
    table('DimProduct',[('product_id','int64'),('category_id','int64'),('product','string'),('list_price_paise','int64'),('unit_cost_paise','int64')])
    table('FactItems',[(n,'string' if n in ['line_id','order_id'] else 'int64') for n in ['line_id','order_id','product_id','quantity','gross_paise','discount_paise','cogs_paise','recognized_units','sales_before_refund_paise','merchandise_margin_paise']])
    model=MODEL/'model.tmdl';text=model.read_text(encoding='utf-8')
    for name in ['DimProduct','FactItems']:
        if 'ref table '+name+'\n' not in text:text+='\nref table '+name+'\n'
    model.write_text(text,encoding='utf-8')
    relations=MODEL/'relationships.tmdl';text=relations.read_text(encoding='utf-8')
    for key,a,b in [('commerce_orders_items','FactItems.order_id','FactOrders.order_id'),('commerce_product_items','FactItems.product_id','DimProduct.product_id')]:
        if 'relationship '+key not in text:text+=f'\nrelationship {key}\n\tfromColumn: {a}\n\ttoColumn: {b}\n'
    relations.write_text(text,encoding='utf-8')

def main(update_semantics=True):
    if update_semantics:update_model()
    templates={}
    for path in PAGES.glob('*/visuals/*/visual.json'):
        obj=json.loads(path.read_text(encoding='utf-8'));kind=obj['visual']['visualType']
        if kind in ['card','slicer','lineChart','barChart','tableEx'] and kind not in templates:templates[kind]=obj
    schema=templates['card']['$schema']
    def visual(page,key,kind,title,pos,roles,sort=None):
        template_kind='barChart' if kind in ['donutChart','clusteredBarChart','clusteredColumnChart'] else kind
        obj=copy.deepcopy(templates[template_kind]);obj['name']=oid(page.name+'-'+key)
        obj.pop('filterConfig',None)
        obj.pop('filters',None)
        obj['position']={'x':pos[0],'y':pos[1],'width':pos[2],'height':pos[3],'z':10,'tabOrder':10}
        obj['annotations']=[{'name':'DecisionStudioBasePosition','value':json.dumps({**obj['position'],'x':pos[0]-224,'y':pos[1]-104})}]
        v=obj['visual'];v['visualType']=kind;v['query']={'queryState':{role:{'projections':[projection(*p) for p in values]} for role,values in roles.items()}}
        if kind=='tableEx':
            for projection_value in v['query']['queryState']['Values']['projections']:projection_value.pop('active',None)
        v.pop('filterConfig',None)
        if sort:v['query']['sortDefinition']={'sort':[{'field':field(*sort),'direction':'Descending'}],'isDefaultSort':False}
        v['visualContainerObjects']['title'][0]['properties']['text']=style_report.lit(title)
        if kind=='slicer':v['objects']={}
        if kind=='donutChart':v['objects']={}
        if kind=='card':
            v['objects']={'labels':[{'properties':{'fontSize':style_report.lit(25),'labelDisplayUnits':style_report.lit(1),'labelPrecision':style_report.lit(1 if '%' in title else 0)}}],'categoryLabels':[{'properties':{'show':style_report.lit(False)}}]}
        save(page/'visuals'/obj['name']/'visual.json',obj)
    pages=[]
    specs=[
      ('Channel economics',[('DimDate','month'),('DimChannel','channel')],
       [('Net sales','Net Sales'),('After marketing','Contribution After Marketing'),('Marketing spend','Marketing Spend'),('After-marketing margin %','After Marketing Margin')],
       [('barChart','Contribution after marketing by channel',('DimChannel','channel'),['Contribution After Marketing']),('lineChart','Contribution and spend over time | INR',('DimDate','month'),['Contribution After Marketing','Marketing Spend'])],
       [('DimChannel','channel',False),('FactOrders','Orders',True),('FactOrders','Net Sales',True),('FactOrders','Marketing Spend',True),('FactOrders','Contribution After Marketing',True),('FactOrders','Marketing Per Placed Order',True),('FactOrders','Negative Contribution Exposure',True)]),
      ('Promotion diagnostics',[('DimDate','month'),('DimCategory','category'),('DimChannel','channel'),('FactOrders','discount_band')],
       [('Gross recognized sales','Gross Sales'),('Discounts','Discounts'),('Discount / gross %','Discount Rate'),('Contribution margin %','Contribution Margin Before Marketing')],
       [('clusteredBarChart','Sales and contribution by discount band | INR',('FactOrders','discount_band'),['Net Sales','Contribution Before Marketing']),('clusteredColumnChart','Mature return rate by discount band',('FactOrders','discount_band'),['Mature Return Rate'])],
       [('FactOrders','discount_band',False),('FactOrders','Orders',True),('FactOrders','Net Sales',True),('FactOrders','Contribution Before Marketing',True),('FactOrders','Mature Orders',True),('FactOrders','Mature Return Rate',True),('FactOrders','Negative Order Rate',True)]),
      ('Payment and fulfilment',[('DimDate','month'),('DimCustomer','region'),('FactOrders','payment_method'),('FactOrders','status')],
       [('Shipped orders','Shipped Orders'),('Fulfilment / shipped order','Fulfilment Per Shipped Order'),('Fees / delivered order','Fees Per Delivered Order'),('Cancellation rate %','Cancellation Rate')],
       [('donutChart','Placed-order payment mix',('FactOrders','payment_method'),['Orders']),('lineChart','Service-cost components over time | INR',('DimDate','month'),['Fulfilment','Fees','Reverse Logistics'])],
       [('FactOrders','payment_method',False),('FactOrders','status',False),('FactOrders','Orders',True),('FactOrders','Variable Service Cost',True),('FactOrders','Service Cost Per Placed Order',True),('FactOrders','Contribution Before Marketing',True),('FactOrders','Negative Order Rate',True)]),
      ('Product and baskets',[('DimDate','month'),('DimCategory','category'),('DimChannel','channel'),('DimProduct','product')],
       [('Item sales | pre-refund','Item Sales Before Refund'),('Item margin | pre-refund','Item Merchandise Margin'),('Merchandise margin %','Item Merchandise Margin Rate'),('Recognized units','Recognized Units')],
       [('barChart','Item sales by category | before refunds',('DimCategory','category'),['Item Sales Before Refund']),('lineChart','Item sales and merchandise margin | INR',('DimDate','month'),['Item Sales Before Refund','Item Merchandise Margin'])],
       [('DimProduct','product',False),('FactOrders','Recognized Units',True),('FactOrders','Delivered Item Orders',True),('FactOrders','Item Sales Before Refund',True),('FactOrders','Item Merchandise Margin',True),('FactOrders','Item Merchandise Margin Rate',True),('FactOrders','Units Per Item Order',True)])]
    for title,slicers,cards,charts,columns in specs:
        pid='ReportSection'+oid(title);page=PAGES/pid;pages.append(pid)
        save(page/'page.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json','name':pid,'displayName':title,'displayOption':'FitToPage','height':1016,'width':1664})
        for i,(table,col) in enumerate(slicers):
            width=(1392-12*(len(slicers)-1))/len(slicers)
            visual(page,'slicer-'+col,'slicer',col.replace('_',' ').title(),(248+i*(width+12),116,width,80),{'Values':[(table,col,False)]})
        for i,(label,measure) in enumerate(cards):visual(page,'card-'+measure,'card',label,(248+i*352,208,336,106),{'Values':[('FactOrders',measure,True)]})
        for i,(kind,label,category,measures) in enumerate(charts):
            actual=kind
            visual(page,'chart-'+str(i),actual,label,(248+i*704,334,688,300),{'Category':[(category[0],category[1],False)],'Y':[('FactOrders',m,True) for m in measures]},sort=None if actual in ['lineChart','donutChart'] else ('FactOrders',measures[0],True))
        visual(page,'details','tableEx',{'Channel economics':'Channel economics | date/channel spend only','Promotion diagnostics':'Discount-band diagnostics | descriptive comparisons','Payment and fulfilment':'Payment and status economics | all placed orders retained','Product and baskets':'Product merchandise economics | excludes refunds and shared costs'}[title],(248,658,1392,312),{'Values':columns},sort=('FactOrders','Item Sales Before Refund' if title=='Product and baskets' else 'Orders',True))
    meta=PAGES/'pages.json';obj=json.loads(meta.read_text(encoding='utf-8'));original=[p for p in obj['pageOrder'] if p not in pages]
    evidence=[p for p in original if json.loads((PAGES/p/'page.json').read_text())['displayName']=='Order evidence']
    obj['pageOrder']=[p for p in original if p not in evidence]+pages+evidence;save(meta,obj)
    style_report.main()
    print('Authored four additional commerce dashboards with native slicers and cross-filtering.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report-only',action='store_true');args=parser.parse_args();main(not args.report_only)
