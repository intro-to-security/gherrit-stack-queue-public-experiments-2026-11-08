"""Read-only exact identity, layer patch and tree checks after native queue work."""
import sys,json,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab import Lane,save,now,ROOT
L=Lane('native');rows={}
def raw_git(*args):
 r=subprocess.run(['git','-C',str(L.gitdir),*args],capture_output=True);assert r.returncode==0,r.stderr;return r.stdout
def author_message(sha):
 headers,message=raw_git('cat-file','commit',sha).split(b'\n\n',1);return next(x for x in headers.splitlines()if x.startswith(b'author ')),message
for name in ['prefix-happy','fresh-enabled','late-group-failure','failed-upper-admission']:
 c=L.get_fixture(name);path=L.evidence/(name+'-final.snapshot.json')
 s=json.loads(path.read_text())if path.exists()else L.snapshot(c,name+'-final')
 refs=dict(line.split('\t')[::-1]for line in s['refs'].splitlines())
 checks={key:{} for key in ['head_ref_agreement','archive_exact','canonical_identity','layer_patch','author_message']}
 for x,n in c['prs'].items():
  pr=s['prs'][x]['data'];original=c['heads'][x]['sha'];current=refs['refs/heads/'+c['heads'][x]['ref']]
  create=json.loads((L.evidence/(name+'-create-'+x+'.receipt.json')).read_text())['data']
  checks['head_ref_agreement'][x]=pr['head']['sha']==current
  checks['archive_exact'][x]=refs['refs/tags/'+c['prefix']+'/authored/'+x+'/v1']==original
  checks['canonical_identity'][x]=pr['node_id']==create['node_id']
  if not pr['merged']:
   oldparent=L.git('rev-parse',original+'^');newparent=L.git('rev-parse',current+'^')
   checks['layer_patch'][x]=raw_git('diff','--binary',oldparent,original)==raw_git('diff','--binary',newparent,current)
   checks['author_message'][x]=author_message(original)==author_message(current)
 merged=[x for x in c['prs']if s['prs'][x]['data']['merged']];top=merged[-1]if merged else None
 trunk=refs['refs/heads/'+c['trunk']]
 checks['trunk_expected_tree']=L.git('rev-parse',trunk+'^{tree}')==L.git('rev-parse',(c['heads'][top]['sha']if top else c['trunk_sha'])+'^{tree}')
 rows[name]={'checks':checks,'merged_letters':merged,'trunk':trunk,'snapshot':str(path.relative_to(ROOT))}
 save(L.home/'artifact-verification.json',{'at':now(),'fixtures':rows,'limits':'Finite current observations; exact retained-input and patch/tree comparisons, not provider settlement.'})
 assert checks['trunk_expected_tree'] and all(all(v.values())for v in checks.values()if isinstance(v,dict)),checks
 print(name,merged,'all comparison checks passed',flush=True)
