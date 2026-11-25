"""Export the current native model's measures as readable DAX documentation."""
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'powerbi/DecisionStudio.SemanticModel/definition/tables/FactOrders.tmdl').read_text(encoding='utf-8')
measures=[name.strip("'")+' =\n'+expression for name,expression in re.findall(r'^\tmeasure (.+?) = (.*)$',source,re.M)]
(root/'powerbi/measures.dax').write_text('\n\n'.join(measures)+'\n',encoding='utf-8')
print('Exported',len(measures),'measures from native TMDL.')
