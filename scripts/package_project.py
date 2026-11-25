"""Package the committed project, excluding local caches and credentials."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'dist/Margin_Atlas_Decision_Studio_Complete.zip');a=p.parse_args()
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    if status.strip():raise ValueError('Commit project changes before packaging')
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0')
    files=[f for f in files if f]
    assert 'powerbi/MarginAtlasDecisionStudio_Premium.pbix' in files
    assert all(not any(part in ['tmp','.git','.pbi','.venv'] for part in Path(f).parts) for f in files)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest={'git_commit':commit,'file_count':len(files),'sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}}
    with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for f in files:z.write(ROOT/f,'Margin-Atlas-Decision-Studio/'+f)
        z.writestr('Margin-Atlas-Decision-Studio/DELIVERY_MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(a.output) as z:assert z.testzip() is None
    summary={'file':str(a.output.resolve()),'bytes':a.output.stat().st_size,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'tracked_files':len(files),'git_commit':commit}
    a.output.with_suffix('.sha256.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
