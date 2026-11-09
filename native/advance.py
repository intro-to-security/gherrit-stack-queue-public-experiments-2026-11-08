"""Release only a checked, actual merge-group SHA in an owned native fixture."""
import sys,json,time,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import L,REPO,good,queue,save,now

def advance(name,seconds=180):
 c=L.get_fixture(name);assert c
 target=L.home/(name+'-advance.json');old=json.loads(target.read_text())if target.exists()else {'case':c,'observations':[],'releases':[]}
 start=time.monotonic()
 while time.monotonic()-start<seconds:
  q=queue(c,name+'-advance-queue');row={'at':now(),'queue':q,'checks':{}}
  nodes=(q or{}).get('entries',{}).get('nodes',[])
  for entry in nodes:
   head=(entry.get('headCommit')or{}).get('oid')
   if not head:continue
   checks=good(L.api(name+'-group-checks-'+head[:10],'GET',f'repos/{REPO}/commits/{head}/check-runs',fresh=True),[200]);row['checks'][head]=checks
   candidates=[x for x in checks['check_runs']if x['name']=='queue-observe' and x['head_sha']==head]
   successful=[x for x in candidates if x['conclusion']=='success' and x['status']=='completed']
   if successful and head not in {x['sha']for x in old['releases']}:
    runid=re.search(r'/actions/runs/(\d+)',successful[0]['details_url']).group(1)
    run=good(L.api(name+'-group-run-'+runid,'GET',f'repos/{REPO}/actions/runs/{runid}',fresh=True),[200])
    assert run['event']=='merge_group' and run['head_sha']==head,(run['event'],run['head_sha'],head)
    statuses=good(L.api(name+'-group-statuses-'+head[:10],'GET',f'repos/{REPO}/commits/{head}/status',fresh=True),[200]);row.setdefault('statuses_before_release',{})[head]=statuses
    release=good(L.status(name+'-group-release-'+head[:12],head,'success'),[201]);old['releases'].append({'at':now(),'sha':head,'check_run':successful[0]['id'],'workflow_run':runid,'status_id':release['id']})
  old['observations'].append(row);save(target,old)
  print(name,[(x['pullRequest']['number'],x['state'],x.get('headCommit'))for x in nodes],flush=True)
  if not nodes:break
  time.sleep(3)
 label=name+'-after-advance-'+str(len(old['observations']));old['after']=L.snapshot(c,label)
 receipt_file=L.home/('happy-results.json'if name=='prefix-happy'else name+'-results.json')
 uuid=json.loads(receipt_file.read_text())['request']['data']['details']['uuid']
 old['original_receipt_after']=L.api(name+'-original-after','GET',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async/{uuid}",fresh=True)
 save(target,old)
 print('ENDED',name,{x:(v['data']['state'],v['data']['merged'])for x,v in old['after']['prs'].items()},flush=True)

if __name__=='__main__':advance(sys.argv[1],int(sys.argv[2])if len(sys.argv)>2 else 180)
