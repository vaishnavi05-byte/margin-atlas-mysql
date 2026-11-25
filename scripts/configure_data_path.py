"""Point the editable PBIP at this checkout's data; native PBIX is self-contained."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'powerbi').glob('*.SemanticModel/definition/expressions.tmdl'):
    text=p.read_text(encoding='utf-8')
    text=re.sub(r'expression DataFolder = "[^"]*"',lambda _: 'expression DataFolder = "'+str(ROOT/'data/powerbi')+'"',text)
    p.write_text(text,encoding='utf-8')
print('Configured local data folder.')
