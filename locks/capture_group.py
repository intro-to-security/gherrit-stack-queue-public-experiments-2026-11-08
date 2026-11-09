#!/usr/bin/env python3
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from lab import Lane,REPO,save,now
L=Lane('locks');result=json.loads((L.home/'results.json').read_text());heads={x['oid'] for x in result['group_heads_before_unstack'] if x}
observations=[]
for n,sha in enumerate(sorted(heads)):
 prefix='queued-members-retained-group-'+str(n)
 commit=L.api(prefix+'-commit','GET','repos/'+REPO+'/git/commits/'+sha,fresh=True)
 statuses=L.api(prefix+'-statuses','GET','repos/'+REPO+'/commits/'+sha+'/status',fresh=True)
 checks=L.api(prefix+'-checks','GET','repos/'+REPO+'/commits/'+sha+'/check-runs?per_page=100',fresh=True)
 observation={'sha':sha,'commit':commit,'statuses':statuses,'checks':checks,'captured_at':now()}
 if commit['http']==200:
  tree=commit['data']['tree']['sha'];observation['tree']=L.api(prefix+'-tree','GET','repos/'+REPO+'/git/trees/'+tree+'?recursive=1',fresh=True)
  fetched=L.git('fetch','--no-write-fetch-head','origin',sha,check=False)
  observation['local_fetch']={'exit':fetched.returncode,'stdout':fetched.stdout,'stderr':fetched.stderr}
  if fetched.returncode==0:
   ref='refs/experiment-inputs/queued-members-group-'+str(n)
   L.git('update-ref',ref,sha,'');observation['local_retained_ref']=ref
 observations.append(observation)
save(L.home/'retained-queue-groups.json',observations)
print(json.dumps([{'sha':x['sha'],'commit_http':x['commit']['http'],'status_state':(x['statuses'].get('data') or {}).get('state'),'local_retained_ref':x.get('local_retained_ref')} for x in observations],indent=2))
