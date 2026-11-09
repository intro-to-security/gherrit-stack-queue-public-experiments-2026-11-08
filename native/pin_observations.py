"""Retain observed native source/candidate commits without changing remote refs."""
import json,re,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab import Lane,save,now
L=Lane('native');seen=set()
def add(value):
 if isinstance(value,str)and re.fullmatch('[0-9a-f]{40}',value):seen.add(value)
def walk(value):
 if isinstance(value,dict):
  for key,item in value.items():
   if key in ('head','base')and isinstance(item,dict):add(item.get('sha'))
   if key in ('headCommit','baseCommit','beforeCommit','afterCommit','potentialMergeCommit','commit')and isinstance(item,dict):add(item.get('oid'))
   if key=='head_sha':add(item)
   walk(item)
 elif isinstance(value,list):
  for item in value:walk(item)
for path in L.evidence.glob('*.json'):
 try:walk(json.loads(path.read_text()))
 except (ValueError,UnicodeError):continue
missing=[sha for sha in sorted(seen)if subprocess.run(['git','-C',str(L.gitdir),'cat-file','-e',sha+'^{commit}'],capture_output=True).returncode]
if missing:
 result=L.git('fetch','origin',*missing,check=False);save(L.evidence/'observed-commit-fetch.json',{'at':now(),'requested':missing,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr});assert result.returncode==0,result.stderr
for sha in sorted(seen):
 L.git('cat-file','-e',sha+'^{commit}');L.git('update-ref','refs/observed-inputs/'+sha,sha)
save(L.home/'pinned-observations.json',{'at':now(),'commits':sorted(seen),'fetched_missing':missing,'remote_mutations':0,'scope':'Observed commit identities from this native lane only; trees/blobs retained transitively in its local Git object store.'});print('Pinned',len(seen),'observed commits;',len(missing),'fetched missing.')
