"""Explicitly requeue a known-ejected upper review at its new hosted head."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import L,REPO,good,pr_state,queue,save,now

def requeue(name):
 c=L.get_fixture(name);prior=json.loads((L.home/(name+'-advance.json')).read_text());assert all(not (prior['after']['prs'][x]['data']['merged'])for x in ['B']);assert prior['after']['prs']['A']['data']['merged']
 q=queue(c,name+'-before-explicit-requeue');assert q['entries']['nodes']==[],q
 p=good(L.api(name+'-requeue-source','GET',f"repos/{REPO}/pulls/{c['prs']['B']}",fresh=True),[200]);assert p['state']=='open' and not p['merged'];assert p['head']['sha']!=c['heads']['B']['sha'];assert p['base']['ref']==c['trunk']
 for kind,sha in [('head',p['head']['sha']),('testmerge',p.get('merge_commit_sha'))]:
  if sha:good(L.status(name+'-requeue-admission-'+kind,sha,'success'),[201])
 rows=[]
 for i in range(30):
  row=pr_state(c,name+'-requeue-ready-'+str(i));rows.append(row);state=row['B'].get('data',{}).get('repository',{}).get('pullRequest',{}).get('mergeStateStatus');print(name,'B',state,flush=True)
  if state=='CLEAN':break
  time.sleep(2)
 save(L.home/(name+'-requeue-ready.json'),rows);assert state=='CLEAN',state
 req=L.api(name+'-explicit-requeue','PUT',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async",{'merge_action':'merge_queue','sha':p['head']['sha']});d=good(req,[200,202]);uuid=d['details']['uuid'];polls=[]
 for i in range(20):
  r=L.api(name+'-requeue-poll-'+str(i),'GET',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async/{uuid}",fresh=True);polls.append(r);s=good(r,[200])['status'];print(name,s,flush=True)
  if s!='pending':break
  time.sleep(1)
 save(L.home/(name+'-requeue-results.json'),{'case':c,'current_head':p['head']['sha'],'request':req,'polls':polls,'queue':queue(c,name+'-requeued'),'scope':'New explicit operation after observed ejection; no branch publication or new authored archive','at':now()})
 print('REQUEUED',name,flush=True)

if __name__=='__main__':requeue(sys.argv[1])
