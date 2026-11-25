"""Set legible titles, useful saved defaults and exposure-first ordering."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
definition=ROOT/'powerbi/DecisionStudio.Report/definition'
def lit(v):return {'expr':{'Literal':{'Value':"'"+v.replace("'","''")+"'"}}}
def field(table,name):return {'Measure':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
short={'Scenario Return Cost Base':'Eligible return cost','Modeled Avoided Return Cost':'Modeled avoided cost','Modeled Net Contribution Change':'Modeled net change','Break Even Cost Per Mature Order':'Break-even cost / order','Contribution Before Marketing':'Contribution | before marketing','Contribution Margin Before Marketing':'Contribution margin'}
defaults={'Metric':('Label','Net sales'),'MinimumSample':('Orders',100)}
for path in (definition/'pages').glob('*/visuals/*/visual.json'):
    obj=json.loads(path.read_text(encoding='utf-8'));v=obj['visual'];kind=v['visualType'];q=v.get('query',{}).get('queryState',{})
    if kind=='card':
        name=q['Values']['projections'][0]['field']['Measure']['Property']
        if name in short:v['visualContainerObjects']['title'][0]['properties']['text']=lit(short[name])
        if 'Rate' in name or 'Margin' in name:v['objects']['labels'][0]['properties']['labelPrecision']={'expr':{'Literal':{'Value':'1D'}}}
    if kind=='slicer':
        col=q['Values']['projections'][0]['field']['Column'];table=col['Expression']['SourceRef']['Entity']
        labels={'Metric':'Trend metric','Recovery':'Cost avoidance (%)','InterventionCost':'Cost / mature order (INR)','MinimumSample':'Minimum mature sample'}
        if table in labels:v['visualContainerObjects']['title'][0]['properties']['text']=lit(labels[table])
        if table in defaults:
            prop,value=defaults[table]
            expr={'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':prop}}
            literal={'Literal':{'Value':str(value)+'L' if isinstance(value,int) else "'"+value+"'"}}
            f={'Version':2,'From':[{'Name':'s','Entity':table,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[expr],'Values':[[literal]]}}}]}
            v.setdefault('objects',{})['general']=[{'properties':{'filter':{'filter':f}}}]
    projections=q.get('Values',{}).get('projections',[])
    has_rank=any('Priority Rank'==p.get('field',{}).get('Measure',{}).get('Property') for p in projections)
    if kind=='tableEx' and has_rank:
        v['query']['sortDefinition']={'sort':[{'field':field('FactOrders','Negative Contribution Exposure'),'direction':'Descending'}],'isDefaultSort':False}
    if kind=='barChart' and any('Negative Contribution Exposure'==p.get('field',{}).get('Measure',{}).get('Property') for p in q.get('Y',{}).get('projections',[])):
        v['query']['sortDefinition']={'sort':[{'field':field('FactOrders','Negative Contribution Exposure'),'direction':'Descending'}],'isDefaultSort':False}
    if kind in ['lineChart','barChart','columnChart']:
        for axis in ['categoryAxis','valueAxis']:
            v.setdefault('objects',{}).setdefault(axis,[{'properties':{}}])[0]['properties']['showAxisTitle']={'expr':{'Literal':{'Value':'false'}}}
    path.write_text(json.dumps(obj,indent=2),encoding='utf-8')
print('Set readable titles, Net sales / 100-order defaults and descending exposure order.')
for path,schema in [(ROOT/'powerbi/DecisionStudio.pbip','https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json'),(definition.parent/'definition.pbir','https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json')]:
    obj=json.loads(path.read_text(encoding='utf-8'));obj['$schema']=schema;path.write_text(json.dumps(obj,indent=2),encoding='utf-8')
