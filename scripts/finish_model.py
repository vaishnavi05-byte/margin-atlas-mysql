"""Add a disconnected sensitivity axis without altering the report's selected assumption."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
definition=ROOT/'powerbi/DecisionStudio.SemanticModel/definition'
axis=definition/'tables/SensitivityRecovery.tmdl'
axis.write_text('''table SensitivityRecovery
\tcolumn Percent
\t\tdataType: int64
\t\tsummarizeBy: none
\t\tsourceColumn: Percent

\tpartition SensitivityRecovery = m
\t\tmode: import
\t\tsource = #table(type table [Percent=Int64.Type],{{0},{5},{10},{15},{20},{25},{30},{35},{40}})
''',encoding='utf-8')
model=definition/'model.tmdl';text=model.read_text(encoding='utf-8')
if 'ref table SensitivityRecovery' not in text: model.write_text(text+'\nref table SensitivityRecovery\n',encoding='utf-8')
fact=definition/'tables/FactOrders.tmdl';text=fact.read_text(encoding='utf-8')
block='''\tmeasure 'Sensitivity Net Change' = [Scenario Return Cost Base] * DIVIDE(SELECTEDVALUE(SensitivityRecovery[Percent]),100) - [Scenario Intervention Cost]
\t\tformatString: "INR "#,0;("INR "#,0);"INR "0

'''
if "measure 'Sensitivity Net Change'" not in text:
    text=text.replace('\tmeasure Orders =',block+'\tmeasure Orders =',1)
fact.write_text(text,encoding='utf-8')
page=ROOT/'powerbi/DecisionStudio.Report/definition/pages/ReportSectiond1a1c362651af80e00f3edf9'
for path in (page/'visuals').glob('*/visual.json'):
    obj=json.loads(path.read_text(encoding='utf-8'))
    if obj['visual']['visualType'] in ['lineChart','columnChart']:
        obj['visual']['visualType']='lineChart'
        q=obj['visual']['query']['queryState']
        q['Category']['projections'][0]={'field':{'Column':{'Expression':{'SourceRef':{'Entity':'SensitivityRecovery'}},'Property':'Percent'}},'queryRef':'SensitivityRecovery.Percent','nativeQueryRef':'Percent'}
        q['Y']['projections'][0]={'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'FactOrders'}},'Property':'Sensitivity Net Change'}},'queryRef':'FactOrders.Sensitivity Net Change','nativeQueryRef':'Sensitivity Net Change'}
        path.write_text(json.dumps(obj,indent=2),encoding='utf-8')
print('Added a full 0–40% sensitivity curve independent of the scenario slicer.')
