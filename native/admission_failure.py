"""Check rejection before queue admission when the selected upper PR check fails."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import L,REPO,good,pr_state,queue,rule,save,now
name='failed-upper-admission';c=L.fixture(name,3,files={'C':{'.queue-experiment/FAIL_PR':'synthetic PR-only failure\n'}})
r=good(L.api(name+'-rule','POST',f'repos/{REPO}/rulesets',rule(c,1)),[201]);c['ruleset']=r['id'];L.save_fixture(c)
for x,n in c['prs'].items():
 p=good(L.api(name+'-source-'+x,'GET',f'repos/{REPO}/pulls/{n}',fresh=True),[200])
 for kind,sha in [('head',p['head']['sha']),('testmerge',p.get('merge_commit_sha'))]:
  if sha:good(L.status(name+'-source-release-'+x+'-'+kind,sha,'success'),[201])
rows=[]
for i in range(35):
 row=pr_state(c,name+'-ready-'+str(i));states={x:v.get('data',{}).get('repository',{}).get('pullRequest',{}).get('mergeStateStatus')for x,v in row.items()}
 p=good(L.api(name+'-C-current','GET',f"repos/{REPO}/pulls/{c['prs']['C']}",fresh=True),[200]);checks=good(L.api(name+'-C-checks','GET',f"repos/{REPO}/commits/{p['head']['sha']}/check-runs",fresh=True),[200]);failed=[x for x in checks['check_runs']if x['name']=='queue-observe'and x['conclusion']=='failure']
 rows.append({'at':now(),'states':states,'checks':checks});print(states,'failedjob',bool(failed),flush=True)
 if states['A']=='CLEAN' and states['B']=='CLEAN' and failed:break
 time.sleep(3)
save(L.home/(name+'-readiness.json'),rows);assert states['A']=='CLEAN' and states['B']=='CLEAN' and failed
before=L.snapshot(c,name+'-before');req=L.api(name+'-enqueue','PUT',f"repos/{REPO}/pulls/{c['prs']['C']}/merge-async",{'merge_action':'merge_queue','sha':c['heads']['C']['sha']});d=good(req,[200,202]);polls=[]
for i in range(25):
 r=L.api(name+'-poll-'+str(i),'GET',f"repos/{REPO}/pulls/{c['prs']['C']}/merge-async/{d['details']['uuid']}",fresh=True);polls.append(r);s=good(r,[200])['status'];print('async',s,flush=True)
 if s!='pending':break
 time.sleep(1)
after=L.snapshot(c,name+'-after');q=queue(c,name+'-final-queue');save(L.home/(name+'-results.json'),{'case':c,'before':before,'request':req,'polls':polls,'after':after,'queue':q,'refs_unchanged':before['refs']==after['refs'],'all_open_unmerged':all(p['data']['state']=='open'and not p['data']['merged']for p in after['prs'].values())});print('DONE',s,flush=True)
