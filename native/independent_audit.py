#!/usr/bin/env python3
import datetime,hashlib,json,pathlib,re,subprocess
P=pathlib.Path(__file__).resolve().parent;E=P/'evidence';INPUTS={}
def read(path):
 data=path.read_bytes();INPUTS[str(path.relative_to(P))]=hashlib.sha256(data).hexdigest();return json.loads(data)
def git(*args):
 r=subprocess.run(['git','-C',str(P/'git'),*args],capture_output=True,text=True);assert r.returncode==0,(args,r.stderr);return r.stdout.strip()
def git_bytes(*args):
 r=subprocess.run(['git','-C',str(P/'git'),*args],capture_output=True);assert r.returncode==0,(args,r.stderr);return r.stdout
def obj(sha):return {'sha':sha,'tree':git('rev-parse',sha+'^{tree}'),'parents':git('show','-s','--format=%P',sha).split()}
def refs(snapshot,prefix):return {ref:sha for line in snapshot['refs'].splitlines() for sha,ref in [line.split()] if ref.startswith(('refs/heads/'+prefix+'/','refs/tags/'+prefix+'/'))}
CASES=read(P/'fixtures.json');T=read(P/'removal-timelines.json')['prs'];checks={};rows=[];trees=[];timing=[]
for name,source in [('prefix-happy','happy-results.json'),('fresh-enabled','fresh-enabled-results.json'),('late-group-failure','late-group-failure-results.json')]:
 initial=read(P/source);advanced=read(P/(name+'-advance.json'));c=CASES[name];snapshot=advanced['after'];owned=refs(snapshot,c['prefix'])
 assert initial['request']['http']==202
 assert initial['request']['payload']['sha']==c['heads']['B']['sha']
 assert initial['admission_polls'][-1]['data']['status']=='enqueued'
 assert advanced['original_receipt_after']['data']['status']=='enqueued'
 for letter,number in c['prs'].items():
  creation=read(E/(name+'-create-'+letter+'.receipt.json'))['data'];after=snapshot['prs'][letter]['data']
  assert creation['id']==after['id'] and creation['node_id']==after['node_id'] and creation['number']==after['number']==number
  original=c['heads'][letter]['sha'];archive='refs/tags/'+c['prefix']+'/authored/'+letter+'/v1';assert owned[archive]==original
  captured=read(E/(name+'-'+letter+'.commit.json'));assert obj(original)['tree']==captured['tree']
  assert git('rev-parse',archive)==original
  if str(number) in T:assert T[str(number)]['id']==creation['node_id']
  live=owned['refs/heads/'+c['heads'][letter]['ref']]
  if letter in ['B','C']:
   assert obj(live)['tree']==captured['tree']
   original_parent=captured['parent'];new_parent=obj(live)['parents'][0]
   assert git_bytes('diff','--binary',original_parent,original)==git_bytes('diff','--binary',new_parent,live)
   trees.append({'case':name,'letter':letter,'pr':number,'authored':original,'hosted':live,'tree':captured['tree'],'hosted_parent':new_parent,'exact_patch_preserved':True})
  if after['head']['sha']!=live:timing.append({'case':name,'pr':number,'snapshot_start':snapshot['start'],'snapshot_end':snapshot['end'],'pr_read_head':after['head']['sha'],'later_ref_read_head':live})
 landed_letters=[letter for letter in c['heads'] if snapshot['prs'][letter]['data']['merged']]
 expected_trunk_tree=obj(c['heads'][landed_letters[-1]]['sha'])['tree']
 assert obj(owned['refs/heads/'+c['trunk']])['tree']==expected_trunk_tree
 a_number=c['prs']['A'];b_number=c['prs']['B'];a_events=T[str(a_number)]['timelineItems']['nodes'];b_events=T[str(b_number)]['timelineItems']['nodes']
 a_merged=[v for v in a_events if v['__typename']=='MergedEvent'];assert len(a_merged)==1
 landing=a_merged[0]['commit']['oid'];assert obj(landing)['tree']==obj(c['heads']['A']['sha'])['tree']
 b_removals=[v for v in b_events if v['__typename']=='RemovedFromMergeQueueEvent'];assert b_removals[0]['reason']=='invalid_merge_commit'
 assert c['heads']['B']['sha']!=owned['refs/heads/'+c['heads']['B']['ref']]
 rows.append({'case':name,'prs':c['prs'],'initial_uuid':initial['request']['data']['details']['uuid'],'initial_admission':'enqueued','A_landed_commit':landing,'first_B_removal_reason':b_removals[0]['reason'],'first_B_removal_at':b_removals[0]['createdAt'],'A_merged_at':a_merged[0]['createdAt'],'B_removal_reasons':[v['reason'] for v in b_removals],'original_uuid_after_outcome':advanced['original_receipt_after']['data']['status'],'final_recorded_lifecycle':{letter:{'merged':value['data']['merged'],'state':value['data']['state']} for letter,value in snapshot['prs'].items()}})
 checks[name+'-canonical-archives-trees-and-admission']=True
early_fresh=read(E/'fresh-enabled-after-advance-10.snapshot.json')
early_refs=refs(early_fresh,CASES['fresh-enabled']['prefix'])
for letter in 'ABC':
 pr=early_fresh['prs'][letter]['data'];remote=early_refs['refs/heads/'+CASES['fresh-enabled']['heads'][letter]['ref']]
 if pr['head']['sha']!=remote:timing.append({'case':'fresh-enabled','phase':'first-A-landing snapshot','pr':pr['number'],'snapshot_start':early_fresh['start'],'snapshot_end':early_fresh['end'],'pr_read_head':pr['head']['sha'],'later_ref_read_head':remote})
fresh=read(P/'fresh-enabled-requeue-results.json');late=read(P/'late-group-failure-requeue-results.json')
for name,x in [('fresh-enabled',fresh),('late-group-failure',late)]:
 assert x['current_head']!=x['case']['heads']['B']['sha']
 assert x['request']['payload']['sha']==x['current_head'] and x['polls'][-1]['data']['status']=='enqueued'
 assert x['request']['data']['details']['uuid']!=next(v['initial_uuid'] for v in rows if v['case']==name)
 assert not x['queue']['entries']['nodes'][0].get('pullRequest',{}).get('number')==x['case']['prs']['A']
checks['requeues-are-distinct-current-hosted-head-intents']=True
assert T['12']['merged'] is True and any(v['__typename']=='MergedEvent' for v in T['12']['timelineItems']['nodes'])
assert T['16']['merged'] is False
assert [v['reason'] for v in T['16']['timelineItems']['nodes'] if v['__typename']=='RemovedFromMergeQueueEvent']==['invalid_merge_commit','failed_checks']
checks['B12-eventually-lands-B16-later-fails']=True
happy=read(P/'happy-results.json');assert len(happy['build_observations'])==40
assert not any(e.get('headCommit') for row in happy['build_observations'] for e in row['queue']['entries']['nodes'])
correction=read(P/'build-stage-interpretation.json');assert correction['observed_group'] is False
later=read(E/'prefix-happy-group-run-42544721015.receipt.json')['data'];assert later['event']=='merge_group' and later['head_sha']=='964781d850b7c100efbea59663f9eb9d1dfdb971' and later['conclusion']=='success'
checks['early-no-group-window-not-permanent-nondispatch']=True
failure=read(P/'failed-upper-admission-results.json');assert failure['request']['http']==202 and failure['polls'][-1]['data']['status']=='failed'
assert failure['queue']['entries']['nodes']==[]
c=failure['case'];assert refs(failure['before'],c['prefix'])==refs(failure['after'],c['prefix'])
for letter,value in failure['after']['prs'].items():
 assert value['data']['state']=='open' and not value['data']['merged'];assert value['data']['head']['sha']==c['heads'][letter]['sha']
 creation=read(E/(c['name']+'-create-'+letter+'.receipt.json'))['data'];assert creation['id']==value['data']['id'] and creation['node_id']==value['data']['node_id']
source_checks=read(E/'failed-upper-C-source-checks.receipt.json')['data']['check_runs'];assert any(x['head_sha']==c['heads']['C']['sha'] and x['name']=='queue-observe' and x['conclusion']=='failure' for x in source_checks)
checks['failing-selected-source-check-rejected-before-admission']=True
ind=P/'independent-audit-evidence';group=read(ind/'requeued-B16-group-commit.json')['data'];gc=read(ind/'requeued-B16-group-checks.json')['data'];run=read(ind/'requeued-B16-failed-run.json')
assert group['tree']['sha']==obj(late['current_head'])['tree']
assert run['event']=='merge_group' and run['head_sha']=='3309d1cb9083bd35bd81fe7330cad225f239315e' and run['conclusion']=='failure'
assert any(x['name']=='queue-observe' and x['head_sha']==run['head_sha'] and x['conclusion']=='failure' for x in gc['check_runs'])
log=(ind/'requeued-B16-failed-run.log').read_text();assert 'Synthetic failure marker present: .queue-experiment/FAIL_MERGE_GROUP' in log
checks['post-requeue-B16-has-actual-intended-MG-failure']=True
manual=[]
for name,new_head,prefix in [('prefix-happy',T['2']['headRefOid'],'happy-source-release-'),('fresh-enabled',fresh['current_head'],'fresh-enabled-admission-'),('late-group-failure',late['current_head'],'late-group-failure-admission-')]:
 targetset=set()
 for file in E.glob(prefix+'*.receipt.json'):
  receipt=read(file)
  if receipt.get('method')=='POST' and '/statuses/' in receipt.get('path','') and receipt.get('payload',{}).get('context')=='experiment/queue-release':targetset.add(receipt['path'].rsplit('/',1)[1])
 assert targetset and new_head not in targetset
 manual.append({'case':name,'original_gate_targets':sorted(targetset),'rewritten_B_head':new_head,'rewritten_head_not_covered_by_original_gate_writes':True})
checks['manual-gate-context-is-a-real-extra-variable']=True
control_path=P.parent/'ci/native-no-manual-gate/state.json'
control_bytes=control_path.read_bytes();INPUTS['../ci/native-no-manual-gate/state.json']=hashlib.sha256(control_bytes).hexdigest();control=json.loads(control_bytes)
assert control['synthetic_status_writes']==0
required=next(x['parameters']['required_status_checks'] for x in control['rule']['rules'] if x['type']=='required_status_checks')
assert required==[{'context':'queue-observe','integration_id':15368}]
assert next(x['parameters']['merge_method'] for x in control['rule']['rules'] if x['type']=='merge_queue')=='SQUASH'
last=control['observations'][-1]['data']
assert last['a']['merged'] is True and last['b']['state']=='OPEN' and not last['b']['merged']
assert last['b']['mergeStateStatus']=='CLEAN' and last['b']['mergeQueueEntry'] is None and not last['mergeQueue']['entries']['nodes']
assert any(x.get('reason')=='invalid_merge_commit' for x in control['removal_events']['B']['data']['node']['timelineItems']['nodes'])
assert any(x['id']==42545595057 and x['head_sha']==last['b']['headRefOid'] and x['event']=='pull_request' and x['conclusion']=='success' for x in control['workflow_runs'])
for source in control['case']['heads'].values():
 markers=subprocess.run(['git','-C',str(P.parent/'ci/git'),'ls-tree','-r',source['sha'],'--','.queue-experiment/FAIL_PR','.queue-experiment/FAIL_MERGE_GROUP'],capture_output=True,text=True)
 assert markers.returncode==0 and not markers.stdout
checks['ungated-SQUASH-reproduces-upper-ejection-with-successful-sync']=True
control_summary={'source':'../ci/native-no-manual-gate/state.json','method':'SQUASH','prs':control['case']['prs'],'only_required_check':required,'synthetic_status_writes':0,'failure_markers_in_authored_heads':False,'A_merged':True,'B_initial_removal':'invalid_merge_commit','B_current_head':last['b']['headRefOid'],'B_after_sync':'CLEAN/open/unqueued','successful_sync_run':42545595057,'conclusion':'The SQUASH observation survives removal of the custom manual gate. No cross-method generalization is established by this control.'}
missing=[]
for file in E.glob('*.intent.json'):
 if not file.with_name(file.name.replace('.intent.json','.receipt.json')).exists():missing.append(file.name)
assert missing==[]
checks['no-unreceipted-API-intents-at-audit-cutoff']=True
output={'audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_checks_passed':all(checks.values()),'cases':rows,'per_layer_tree_patch_checks':trees,'sequential_snapshot_head_disagreements':timing,'manual_gate_confound':manual,'ungated_SQUASH_control':control_summary,'prefix_happy_early_window':{'samples':40,'first':happy['build_observations'][0]['at'],'last':happy['build_observations'][-1]['at'],'no_head_in_window':True,'later_successful_group_run':42544721015,'later_run_created_at':later['created_at']},'failed_admission_terminal':failure['polls'][-1]['data'],'B16_actual_failed_MG_run':42545048985,'root_input_hashes':INPUTS,'scope':'Read-only audit of public synthetic native evidence and local immutable Git objects; no fixture mutation. Additional public GETs/log read only for known B16 group/run; root-authorized public CI SQUASH control read locally.'}
(P/'INDEPENDENT-AUDIT.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'all_checks_passed':output['all_checks_passed'],'checks':checks,'snapshot_disagreements':timing,'tree_rows':len(trees)},indent=2))
