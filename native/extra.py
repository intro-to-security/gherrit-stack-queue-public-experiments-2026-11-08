"""Fresh native queue controls: group failure and an initially enabled queue."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import L,REPO,good,queue,rule,pr_state,save,now

def prepare(name,marker=False):
 c=L.fixture(name,3 if not marker else 2,files={'B':{'.queue-experiment/FAIL_MERGE_GROUP':'synthetic group-only failure\n'}} if marker else None)
 if not (L.evidence/(name+'-before.snapshot.json')).exists():L.snapshot(c,name+'-before')
 r=good(L.api(name+'-rule','POST',f'repos/{REPO}/rulesets',rule(c,1)),[201]);c['ruleset']=r['id'];L.save_fixture(c)
 for x,n in c['prs'].items():
  pr=good(L.api(name+'-source-'+x,'GET',f'repos/{REPO}/pulls/{n}',fresh=True),[200])
  for kind,sha in [('head',pr['head']['sha']),('testmerge',pr.get('merge_commit_sha'))]:
   if sha:good(L.status(name+'-admission-'+x+'-'+kind,sha,'success'),[201])
 rows=[]
 for i in range(35):
  row=pr_state(c,name+'-ready-'+str(i));rows.append(row)
  states={x:v.get('data',{}).get('repository',{}).get('pullRequest',{}).get('mergeStateStatus')for x,v in row.items()};print(name,states,flush=True)
  if all(x=='CLEAN'for x in states.values()):break
  time.sleep(3)
 save(L.home/(name+'-ready.json'),rows);assert all(x=='CLEAN'for x in states.values()),states
 request=L.api(name+'-enqueue','PUT',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async",{'merge_action':'merge_queue','sha':c['heads']['B']['sha']});d=good(request,[202,200]);uuid=d['details']['uuid'];polls=[]
 for i in range(25):
  r=L.api(name+'-poll-'+str(i),'GET',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async/{uuid}",fresh=True);polls.append(r);s=good(r,[200])['status'];print('async',s,flush=True)
  if s!='pending':break
  time.sleep(1)
 q=queue(c,name+'-queued');save(L.home/(name+'-results.json'),{'case':c,'request':request,'admission_polls':polls,'initial_queue':q,'prepared_at':now()});print('PREPARED',name,c['prs'],q,flush=True)

if __name__=='__main__':prepare(sys.argv[1],marker=sys.argv[1]=='late-group-failure')
