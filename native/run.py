"""Stage one queue-prefix case; each invocation resumes only acknowledged effects."""
from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab import Lane,REPO,save,now
L=Lane('native');OUT=L.home/'happy-results.json'
QUERY='''query($owner:String!,$repo:String!,$branch:String!){repository(owner:$owner,name:$repo){mergeQueue(branch:$branch){id url entries(first:100){nodes{id position state enqueuedAt headCommit{oid} baseCommit{oid} pullRequest{id number headRefOid}} pageInfo{hasNextPage endCursor}}}}}'''
def good(r,statuses):
 if r['http'] not in statuses or r.get('parse_error'):raise RuntimeError('Unexpected receipt '+r['label']+': '+str(r['http'])+' '+str(r.get('data'))[:350])
 return r['data']
def queue(c,label):
 r=L.graphql(label,QUERY,{'owner':'intro-to-security','repo':REPO.split('/')[1],'branch':c['trunk']},fresh=True)
 d=good(r,[200]);assert not d.get('errors'),d
 return d['data']['repository']['mergeQueue']
def rule(c,build):
 return {'name':'native-'+c['name'],'target':'branch','enforcement':'active','bypass_actors':[],
 'conditions':{'ref_name':{'include':['refs/heads/'+c['trunk']],'exclude':[]}},
 'rules':[{'type':'merge_queue','parameters':{'check_response_timeout_minutes':5,'grouping_strategy':'ALLGREEN','max_entries_to_build':build,'max_entries_to_merge':5,'merge_method':'SQUASH','min_entries_to_merge':1,'min_entries_to_merge_wait_minutes':1}},
 {'type':'required_status_checks','parameters':{'required_status_checks':[{'context':'queue-observe'},{'context':'experiment/queue-release'}],'strict_required_status_checks_policy':False}}]}
def pr_state(c,label):
 q='''query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$number){id number headRefOid baseRefName state merged mergeStateStatus mergeQueueEntry{id position state headCommit{oid} baseCommit{oid}} commits(last:1){nodes{commit{oid statusCheckRollup{state contexts(first:30){nodes{... on CheckRun{name conclusion status detailsUrl} ... on StatusContext{context state targetUrl}}}}}}}}}}'''
 return {x:good(L.graphql(label+'-'+x,q,{'owner':'intro-to-security','repo':REPO.split('/')[1],'number':n},fresh=True),[200]) for x,n in c['prs'].items()}
def poll(c,label,req):
 d=good(req,[200,202,409]);detail=d.get('details',{});uuid=detail.get('uuid');assert uuid,d
 assert detail.get('merge_action')=='merge_queue' and detail.get('expected_head_sha')==req['payload']['sha'],detail
 rows=[]
 for i in range(25):
  r=L.api(label+'-'+str(i),'GET',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async/{uuid}",fresh=True);rows.append(r)
  status=good(r,[200]).get('status');print('async',status,flush=True)
  if status!='pending':break
  time.sleep(1)
 return rows

def prepare():
 c=L.fixture('prefix-happy',3);before=L.snapshot(c,'happy-before') if not (L.evidence/'happy-before.snapshot.json').exists() else json.loads((L.evidence/'happy-before.snapshot.json').read_text())
 created=good(L.api('happy-rule-create','POST',f'repos/{REPO}/rulesets',rule(c,0)),[201]);c['ruleset']=created['id'];L.save_fixture(c)
 # Admission checks and group checks use the same names, but distinct exact SHAs.
 for x,n in c['prs'].items():
  p=good(L.api('happy-source-'+x,'GET',f'repos/{REPO}/pulls/{n}',fresh=True),[200])
  for kind,sha in [('head',p['head']['sha']),('testmerge',p.get('merge_commit_sha'))]:
   if sha:good(L.status('happy-source-release-'+x+'-'+kind,sha,'success'),[201])
 rows=[]
 for i in range(30):
  row=pr_state(c,'happy-ready-'+str(i));rows.append(row)
  states={x:v.get('data',{}).get('repository',{}).get('pullRequest',{}).get('mergeStateStatus')for x,v in row.items()}
  print('source',states,flush=True)
  if all(v=='CLEAN'for v in states.values()):break
  time.sleep(3)
 save(L.home/'happy-source-ready.json',rows)
 assert all(v=='CLEAN' for v in states.values()),states
 req=L.api('happy-enqueue','PUT',f"repos/{REPO}/pulls/{c['prs']['B']}/merge-async",{'merge_action':'merge_queue','sha':c['heads']['B']['sha']})
 polls=poll(c,'happy-admission',req);q=queue(c,'happy-queued');snap=L.snapshot(c,'happy-after-admission')
 result={'case':c,'before':before,'request':req,'admission_polls':polls,'queue_paused':q,'after_admission':snap,'prepared_at':now()};save(OUT,result)
 print('PREPARED',json.dumps({'prs':c['prs'],'stack':c['stack'],'queue':q}),flush=True)

def build():
 r=json.loads(OUT.read_text());c=r['case'];good(L.api('happy-build-enable','PUT',f"repos/{REPO}/rulesets/{c['ruleset']}",rule(c,1)),[200])
 rows=[]
 for i in range(40):
  q=queue(c,'happy-build-'+str(i));rows.append({'at':now(),'queue':q});nodes=(q or {}).get('entries',{}).get('nodes',[])
  print('queue',[(x['pullRequest']['number'],x['state'],x.get('headCommit'))for x in nodes],flush=True)
  if any(x.get('headCommit')for x in nodes):break
  time.sleep(2)
 r['build_observations']=rows;r['observation_ended_at']=now();r['group_observed']=any(x.get('headCommit')for row in rows for x in (row.get('queue')or{}).get('entries',{}).get('nodes',[]));r['after_build']=L.snapshot(c,'happy-after-build');save(OUT,r)
 print('BUILD OBSERVATION',r['group_observed'],flush=True)

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='build':build()
 else:raise RuntimeError('Unknown stage')
