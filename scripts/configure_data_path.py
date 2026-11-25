"""Point the editable report at this checkout's CSV folder after moving it."""
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'powerbi/DecisionStudio.SemanticModel/definition/expressions.tmdl'
text=path.read_text(encoding='utf-8')
target=str(root/'data/powerbi').replace('"','""')
text=re.sub(r'^expression DataFolder = "[^"]*"',lambda _: 'expression DataFolder = "'+target+'"',text,count=1,flags=re.M)
path.write_text(text,encoding='utf-8')
print('Power BI DataFolder now points to this checkout. Open the PBIP and Refresh.')
