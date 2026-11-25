"""Apply the original Decision Studio visual system to native PBIR source.

Native data roles are retained. Run after building pages, before Desktop reload.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'powerbi/DecisionStudio.Report'
DEF=REPORT/'definition'


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')


def lit(value):
    if isinstance(value,bool): v=str(value).lower()
    elif isinstance(value,str): v="'"+value.replace("'","''")+"'"
    else: v=str(value)+'D'
    return {'expr':{'Literal':{'Value':v}}}


def fill(value):return {'solid':{'color':lit(value)}}


def oid(value):return hashlib.sha256(('ds-design-'+value).encode()).hexdigest()[:20]


def vco(bg=False, color='#FFFFFF'):
    return {'background':[{'properties':{'show':lit(bg),'color':fill(color),'transparency':lit(0)}}],
            'border':[{'properties':{'show':lit(False)}}],
            'visualHeader':[{'properties':{'show':lit(False)}}],
            'padding':[{'properties':{side:lit(0) for side in ['top','bottom','left','right']}}]}


def textbox(page,key,text,x,y,w,h,size=16,fg='#173243',bg=None,bold=False):
    name=oid(page.name+'-'+key)
    paragraphs=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI Semibold' if bold else 'Segoe UI','fontSize':str(size)+'px','color':fg}}],
                 'horizontalTextAlignment':'left'} for line in text.split('\n')]
    obj={'$schema':VISUAL_SCHEMA,'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':0 if key=='sidebar' else 10000,'tabOrder':900},
         'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':paragraphs}}]},
                   'visualContainerObjects':vco(bg is not None,bg or '#FFFFFF')},
         'annotations':[{'name':'DecisionStudioChrome','value':'true'}]}
    save(page/'visuals'/name/'visual.json',obj)


def button(page,key,label,action,x,y,w=184,h=48,target=None,active=False):
    name=oid(page.name+'-'+key)
    link={'show':lit(True),'type':lit(action)}
    if target:link['navigationSection']=lit(target)
    obj={'$schema':VISUAL_SCHEMA,'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':10100,'tabOrder':950},
         'howCreated':'InsertVisualButton',
         'visual':{'visualType':'actionButton','drillFilterOtherVisuals':True,
                   'objects':{
                     'text':[{'properties':{'show':lit(True)}},{'selector':{'id':'default'},'properties':{'text':lit(label),'fontSize':lit(12),'fontFamily':lit('Segoe UI Semibold'),'fontColor':fill('#FFFFFF'),'horizontalAlignment':lit('left'),'verticalAlignment':lit('middle'),'leftMargin':lit(14),'rightMargin':lit(10),'topMargin':lit(0),'bottomMargin':lit(0)}}],
                     'fill':[{'properties':{'show':lit(True)}},{'selector':{'id':'default'},'properties':{'fillColor':fill('#087F8C' if active else '#223F51'),'transparency':lit(0)}},{'selector':{'id':'hover'},'properties':{'fillColor':fill('#146878'),'transparency':lit(0)}}],
                     'outline':[{'properties':{'show':lit(False)}}],
                     'icon':[{'properties':{'show':lit(False)}}],
                     'shape':[{'properties':{'tileShape':lit('rectangleRounded'),'roundEdge':lit(8)}},{'selector':{'id':'default'},'properties':{'tileShape':lit('rectangleRounded')}}]},
                   'visualContainerObjects':{**vco(),'visualLink':[{'properties':link}]}},
         'annotations':[{'name':'DecisionStudioChrome','value':'true'}]}
    save(page/'visuals'/name/'visual.json',obj)


def main():
    global VISUAL_SCHEMA
    pagesmeta=json.loads((DEF/'pages/pages.json').read_text(encoding='utf-8'))
    pids=pagesmeta['pageOrder']
    names={pid:json.loads((DEF/'pages'/pid/'page.json').read_text(encoding='utf-8'))['displayName'] for pid in pids}
    navigation=[(pid,names[pid]) for pid in pids if names[pid]!='Order evidence']
    subtitles={
      'Business pulse':'Follow sales into contribution. Choose a metric, then inspect the mix.',
      'Leakage explorer':'Find where discounts, refunds and variable costs consume contribution.',
      'Delivery signals':'Compare eligible deliveries and mature returns with their sample sizes.',
      'Customer cohorts':'Complete 90-day observation windows. Totals use customer counts.',
      'Decision queue':'Rank observed negative-order contribution. Select a segment and inspect its evidence.',
      'Scenario lab':'Change the assumptions. Intervention costs apply to every mature order selected.',
      'Order evidence':'Order-level evidence for the selected segment and report context.',
      'Channel economics':'Original acquisition channels. Spend is observed by date and channel; this is not causal marketing attribution.',
      'Promotion diagnostics':'Compare discount bands with mature outcomes. Observed promotion differences are not treatment effects.',
      'Payment and fulfilment':'Inspect payment mix, shipped-order costs and cancellation outcomes at the correct grain.',
      'Product and baskets':'Item sales and merchandise margin before refunds and shared order costs. No product profit allocation.'
      ,'Compare periods':'Choose independent baseline and comparison months; retain category, channel and region context.'
    }
    for idx,pid in enumerate(pids):
        page=DEF/'pages'/pid
        pj=json.loads((page/'page.json').read_text(encoding='utf-8'))
        pj['width']=1664;pj['height']=1016
        pj.setdefault('objects',{})['background']=[{'properties':{'color':fill('#F1F6F8'),'transparency':lit(0)}}]
        title=names[pid]
        save(page/'page.json',pj)
        for path in (page/'visuals').glob('*/visual.json'):
            obj=json.loads(path.read_text(encoding='utf-8'))
            annotations=obj.setdefault('annotations',[])
            if any(a['name']=='DecisionStudioChrome' for a in annotations): continue
            VISUAL_SCHEMA=obj['$schema']
            old=next((a for a in annotations if a['name']=='DecisionStudioBasePosition'),None)
            if old: pos=json.loads(old['value'])
            else:
                pos=dict(obj['position']);annotations.append({'name':'DecisionStudioBasePosition','value':json.dumps(pos)})
            obj['position']={**pos,'x':pos['x']+224,'y':pos['y']+104}
            visual=obj['visual']; kind=visual['visualType']; objects=visual.setdefault('objects',{})
            container=visual.setdefault('visualContainerObjects',{})
            container['border']=[{'properties':{'show':lit(False)}}]
            container['visualHeader']=[{'properties':{'show':lit(True)}}]
            if kind=='slicer':
                obj['position']['height']=80
                objects['data']=[{'properties':{'mode':lit('Dropdown')}}]
                fields=visual.get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[])
                table=fields[0]['field'].get('Column',{}).get('Expression',{}).get('SourceRef',{}).get('Entity') if fields else None
                strict=table in ['Metric','Recovery','InterventionCost','MinimumSample']
                objects['selection']=[{'properties':{'strictSingleSelect':lit(strict),'singleSelect':lit(False),'selectAllCheckboxEnabled':lit(not strict)}}]
            if kind=='card':
                measure_name=visual.get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[{}])[0].get('field',{}).get('Measure',{}).get('Property','')
                precision=1 if 'Rate' in measure_name or measure_name in ['Contribution Margin Before Marketing','After Marketing Margin'] else 0
                objects['labels']=[{'properties':{'fontSize':lit(25),'color':fill('#173243'),'labelDisplayUnits':lit(1),'labelPrecision':lit(precision)}}]
                objects['categoryLabels']=[{'properties':{'show':lit(False)}}]
            save(path,obj)
        textbox(page,'sidebar','',0,0,216,1016,bg='#132D3D')
        textbox(page,'brand','MARGIN\nATLAS',22,24,174,96,27,'#FFFFFF',bold=True)
        textbox(page,'studio','DECISION STUDIO',24,116,178,26,12,'#7DD5CD',bold=True)
        textbox(page,'nav-label','WORKSPACE',24,170,170,28,12,'#9FB6C4')
        nav_labels={'Promotion diagnostics':'Promotions','Payment and fulfilment':'Payment & costs','Product and baskets':'Products & baskets'}
        for j,(target_id,nav_title) in enumerate(navigation): button(page,'nav-'+str(j),nav_labels.get(nav_title,nav_title),'PageNavigation',16,196+j*52,h=44,target=target_id,active=target_id==pid)
        button(page,'clear','Clear selections','ClearAllSlicers',16,734,h=44)
        if title=='Order evidence':button(page,'back','Back to selection','Back',16,794,h=44)
        textbox(page,'snapshot','SYNTHETIC DATA\nSnapshot 30 Sep 2026',24,894,174,60,12,'#B5CAD5')
        textbox(page,'title',title,248,22,1110,56,32,bold=True)
        textbox(page,'subtitle',subtitles[title],248,75,1380,28,16,'#4B6677')
        textbox(page,'footer','Contribution excludes fixed overhead and taxes. Scenarios are hypothetical; observed patterns are not causal effects.',248,985,1380,24,12,'#5C7280')
    pagesmeta['$schema']='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json'
    save(DEF/'pages/pages.json',pagesmeta)
    pbip=ROOT/'powerbi/DecisionStudio.pbip';obj=json.loads(pbip.read_text(encoding='utf-8'));obj['$schema']='https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json';save(pbip,obj)
    pbir=REPORT/'definition.pbir';obj=json.loads(pbir.read_text(encoding='utf-8'));obj['$schema']='https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json';save(pbir,obj)
    theme=json.loads((ROOT/'powerbi/decision-studio-theme.json').read_text(encoding='utf-8'))
    theme_name='DecisionStudio-9d22bc51.json'
    theme['name']=theme_name
    theme['visualStyles']={'tableEx':{'*':{'values':[{'fontSize':11}], 'columnHeaders':[{'fontSize':11,'bold':True}], 'grid':[{'rowPadding':5}]}},
        'slicer':{'*':{'header':[{'show':False}]}},
        'lineChart':{'*':{'lineStyles':[{'strokeWidth':3}]}},
        'card':{'*':{'labels':[{'labelDisplayUnits':1}]}}}
    save(REPORT/'StaticResources/RegisteredResources'/theme_name,theme)
    report_path=DEF/'report.json';rj=json.loads(report_path.read_text(encoding='utf-8'))
    rj['themeCollection']['customTheme']={'name':theme_name,'type':'RegisteredResources','reportVersionAtImport':{'visual':'2.15.0','report':'3.4.0','page':'2.1.0'}}
    rj['resourcePackages']=[p for p in rj.get('resourcePackages',[]) if p['name']!='RegisteredResources']+[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':theme_name,'path':theme_name,'type':'CustomTheme'}]}]
    save(report_path,rj)
    # Keep the current premium visual system when older authoring helpers restyle pages.
    if (ROOT/'scripts/premium_design.py').exists():
        import premium_design
        premium_design.premium(REPORT,'MARGIN\nATLAS','#50D5CB','#F28B73','#17263D','SYNTHETIC DATA\nSnapshot 30 Sep 2026',{
            'Compare periods':'Choose a baseline and comparison month. Defaults: Aug vs Sep 2026. Region and category selections apply to both.',
            'Scenario lab':'Adjust hypothetical assumptions. Intervention cost applies to every mature selected order; this is not achieved savings.',
            'Product and baskets':'Item sales and merchandise margin before refunds and shared order costs. Product filters do not allocate order profit.'})
    print(f'Styled {len(pids)} pages with native navigation, reset actions and order-evidence back navigation.')


if __name__=='__main__':main()
