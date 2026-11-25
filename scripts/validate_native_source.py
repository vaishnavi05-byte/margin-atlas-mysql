"""Check native JSON syntax and TMDL field bindings with the standard library.

This does not execute DAX or claim schema coverage. See the separately saved
official Microsoft CLI validation report and native-engine reconciliation.
"""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    definition=ROOT/'powerbi/DecisionStudio.SemanticModel/definition'
    columns={};measures={}
    for path in (definition/'tables').glob('*.tmdl'):
        text=path.read_text(encoding='utf-8');table=re.search(r'^table (.+)$',text,re.M)[1].strip("'")
        columns[table]=set();measures[table]=set()
        for kind,name in re.findall(r"^\t(column|measure) ('(?:[^']|'')*'|[^\s=]+)",text,re.M):
            (columns if kind=='column' else measures)[table].add(name.strip("'").replace("''","'"))
    checked=0; bindings=0
    def inspect(obj):
        nonlocal bindings
        if isinstance(obj,dict):
            for kind,lookup in [('Column',columns),('Measure',measures)]:
                if kind in obj:
                    value=obj[kind];table=value.get('Expression',{}).get('SourceRef',{}).get('Entity')
                    if table:
                        if table not in lookup or value['Property'] not in lookup[table]:raise ValueError((table,value['Property']))
                        bindings+=1
            for value in obj.values():inspect(value)
        elif isinstance(obj,list):
            for value in obj:inspect(value)
    for path in (ROOT/'powerbi').rglob('*'):
        if any(part in ['.pbi'] for part in path.parts) or not path.is_file():continue
        if path.suffix in ['.json','.pbip','.pbir','.pbism']:
            inspect(json.loads(path.read_text(encoding='utf-8-sig')));checked+=1
    relations=(definition/'relationships.tmdl').read_text(encoding='utf-8')
    for table,column in re.findall(r'(?:fromColumn|toColumn): ([^.\n]+)\.([^\n]+)',relations):
        if column.strip("'") not in columns[table.strip("'")]:raise ValueError('Relationship field missing')
    result={'validation_type':'JSON syntax and TMDL field/relationship bindings','documents_checked':checked,'direct_field_bindings_checked':bindings,'model_tables':len(columns),'measures':sum(map(len,measures.values())),'result':'PASS','schema_validation':'See validation-report.json from Microsoft authoring CLI','native_execution':'See docs/native-validation.json'}
    (ROOT/'powerbi/source-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
