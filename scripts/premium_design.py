import json
from pathlib import Path
import style_report as S
save=S.save
def premium(report,brand,accent,secondary,navy,note,subtitles=None):
    S.VISUAL_SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.15.0/schema.json'
    pages=report/'definition/pages';meta=json.loads((pages/'pages.json').read_text(encoding='utf-8'));pids=meta['pageOrder']
    names={pid:json.loads((pages/pid/'page.json').read_text(encoding='utf-8'))['displayName'] for pid in pids}
    nav=[(pid,n) for pid,n in names.items() if n!='Order evidence']
    for index,pid in enumerate(pids):
        p=pages/pid;pj=json.loads((p/'page.json').read_text(encoding='utf-8'));pj.setdefault('objects',{})['background']=[{'properties':{'color':S.fill('#EBEEF7'),'transparency':S.lit(0)}}];save(p/'page.json',pj)
        # Clear only the chrome created by this script; analytical visuals remain intact.
        for path in (p/'visuals').glob('*/visual.json'):
            o=json.loads(path.read_text(encoding='utf-8'));chrome=any(a.get('name')=='DecisionStudioChrome' for a in o.get('annotations',[]))
            if chrome:
                path.unlink();continue
            v=o['visual'];kind=v['visualType'];co=v.setdefault('visualContainerObjects',{});objects=v.setdefault('objects',{})
            co['background']=[{'properties':{'show':S.lit(True),'color':S.fill(navy if kind=='card' else '#FFFFFF'),'transparency':S.lit(0)}}]
            co['border']=[{'properties':{'show':S.lit(True),'color':S.fill(navy if kind=='card' else '#DFE4F0'),'radius':S.lit(12)}}]
            co['padding']=[{'properties':{x:S.lit(12) for x in ['top','bottom','left','right']}}]
            title=co.setdefault('title',[{'properties':{}}])[0]['properties'];title.update({'fontSize':S.lit(13),'fontColor':S.fill('#C9D7EC' if kind=='card' else '#263650'),'fontFamily':S.lit('Segoe UI Semibold')})
            if kind=='card':
                mn=v.get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[{}])[0].get('field',{}).get('Measure',{}).get('Property','')
                large=mn in ['Net Sales','Baseline Sales','Comparison Sales','Sales Change','Contribution Before Marketing','Contribution After Marketing','Negative Contribution Exposure','Marketing Spend','Gross Sales','Discounts','Item Sales Before Refund','Item Merchandise Margin','Merchandise Sales']
                precision=1 if large or any(s in mn for s in ['Rate','Margin','Percent']) else (2 if any(s in mn for s in ['Average','Per','Days']) else 0)
                objects['labels']=[{'properties':{'fontSize':S.lit(27),'color':S.fill('#FFFFFF'),'labelDisplayUnits':S.lit(1000000 if large else 1),'labelPrecision':S.lit(precision)}}]
                objects['categoryLabels']=[{'properties':{'show':S.lit(False)}}]
            if kind=='slicer':
                objects['data']=[{'properties':{'mode':S.lit('Dropdown')}}]
                tables=[f.get('field',{}).get('Column',{}).get('Expression',{}).get('SourceRef',{}).get('Entity') for f in v.get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[])]
                single=any(t in ['Metric','Target','MinimumSample','BaselineMonth','ComparisonMonth','Recovery','InterventionCost'] for t in tables)
                objects['selection']=[{'properties':{'strictSingleSelect':S.lit(single),'singleSelect':S.lit(single),'selectAllCheckboxEnabled':S.lit(not single)}}]
                defaults={'BaselineMonth':'2026-08','ComparisonMonth':'2026-09','Target':5,'MinimumSample':100}
                if 'Metric' in tables:defaults['Metric']='Merchandise sales' if brand.startswith('OLIST') else 'Net sales'
                for t in tables:
                    if t in defaults:
                        col=v['query']['queryState']['Values']['projections'][0]['field']['Column']['Property'];value=defaults[t]
                        literal="'"+value+"'" if isinstance(value,str) else str(value)+'L'
                        objects['general']=[{'properties':{'filter':{'filter':{'Version':2,'From':[{'Name':'s','Entity':t,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':col}}],'Values':[[{'Literal':{'Value':literal}}]]}}}]}}}}]
            save(path,o)
        title=names[pid]
        S.textbox(p,'sidebar','',0,0,216,1016,bg=navy)
        S.textbox(p,'hero','',216,0,1448,104,bg=navy)
        hp=p/'visuals'/S.oid(p.name+'-hero')/'visual.json';ho=json.loads(hp.read_text(encoding='utf-8'));ho['position']['z']=1;save(hp,ho)
        S.textbox(p,'brand',brand,24,26,174,95,27,'#FFFFFF',bold=True)
        S.textbox(p,'studio','ANALYTICS WORKSPACE',24,123,180,26,10,accent,bold=True)
        S.textbox(p,'nav-label','EXPLORE / INVESTIGATE',24,170,180,25,10,'#9DACC8')
        aliases={'Promotion diagnostics':'Promotions','Payment and fulfilment':'Payment & costs','Product and baskets':'Products & baskets'}
        step=46 if len(nav)>8 else 62
        for j,(target,n) in enumerate(nav):
            S.button(p,'nav-'+str(j),f'{j+1:02d}  '+aliases.get(n,n),'PageNavigation',14,204+j*step,w=188,h=40,target=target,active=target==pid)
            bp=p/'visuals'/S.oid(p.name+'-nav-'+str(j))/'visual.json';bo=json.loads(bp.read_text(encoding='utf-8'))
            fills=bo['visual']['objects']['fill'];fills[1]['properties']['fillColor']=S.fill(accent if target==pid else navy);fills[2]['properties']['fillColor']=S.fill('#33445F')
            text=bo['visual']['objects']['text'][1]['properties'];text['fontColor']=S.fill(navy if target==pid else '#D8E2F2');text['fontSize']=S.lit(11);save(bp,bo)
        S.button(p,'clear','Reset page filters','ClearAllSlicers',14,752,w=188,h=42)
        if title=='Order evidence':S.button(p,'back','Back to selection','Back',14,812,w=188,h=42)
        S.textbox(p,'snapshot',note,24,894,176,90,11,'#B4C2DA')
        S.textbox(p,'title',title,248,30,1100,40,28,'#FFFFFF',bold=True)
        subtitle=(subtitles or {}).get(title,'Select a chart to focus the page. Hover for detail; reset page filters to start again.')
        S.textbox(p,'subtitle',subtitle,248,78,1370,25,12,'#C3D3ED')
        S.textbox(p,'page-number',f'{index+1:02d} / {len(pids):02d}',1520,25,120,40,20,accent,bold=True)
        S.textbox(p,'footer','CHARTS CROSS-FILTER  /  HOVER FOR DETAIL  /  CTRL + CLICK NAVIGATION IN DESKTOP',248,985,1392,24,11,'#61718A')
    meta['activePageName']=pids[0];save(pages/'pages.json',meta)
    theme={'name':'PremiumWorkspace.json','dataColors':[accent,secondary,'#708BFF','#E7B450','#BC8AE8','#478DAB'],'background':'#FFFFFF','foreground':'#263650','tableAccent':accent,
      'textClasses':{'label':{'fontFace':'Segoe UI','fontSize':11,'color':'#53647E'},'title':{'fontFace':'Segoe UI Semibold','fontSize':13,'color':'#263650'},'callout':{'fontFace':'Segoe UI Semibold','fontSize':27,'color':navy}},
      'visualStyles':{'tableEx':{'*':{'values':[{'fontSize':11}],'columnHeaders':[{'fontSize':11,'bold':True}],'grid':[{'rowPadding':7}]}},'lineChart':{'*':{'lineStyles':[{'strokeWidth':3}]}},'slicer':{'*':{'header':[{'show':False}]}}}}
    save(report/'StaticResources/RegisteredResources/PremiumWorkspace.json',theme)
    rp=report/'definition/report.json';r=json.loads(rp.read_text(encoding='utf-8'));r['themeCollection']['customTheme']={'name':'PremiumWorkspace.json','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.15.0','report':'3.4.0','page':'2.1.0'}}
    r['resourcePackages']=[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'PremiumWorkspace.json','path':'PremiumWorkspace.json','type':'CustomTheme'}]}];save(rp,r)
