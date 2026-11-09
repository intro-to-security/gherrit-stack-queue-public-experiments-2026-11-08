#!/usr/bin/env python3
import datetime,json,pathlib
P=pathlib.Path(__file__).resolve().parent;E=P/'evidence'
def read(path):return json.loads(path.read_text())
def snap(name):return read(E/(name+'.snapshot.json'))
def owned_refs(snapshot):
 return {ref:sha for line in snapshot['refs'].splitlines() for sha,ref in [line.split()] if ref.startswith(('refs/heads/exp/locks/','refs/tags/exp/locks/'))}
x=read(P/'results.json');case=x['case'];assert x['phase']=='complete'
assert x['ruleset']['conditions']['ref_name']=={'include':['refs/heads/'+case['trunk']],'exclude':[]}
assert x['ruleset']['bypass_actors']==[]
queue_rule=next(v for v in x['ruleset']['rules'] if v['type']=='merge_queue')
assert queue_rule['parameters']['max_entries_to_build']==1
assert x['admission_request']['http']==202
assert x['admission_terminal']['data']['status']=='enqueued'
assert x['uuid']=='70ce4b4f-8a53-4c09-affb-1785fd245cd3'
assert all(x['preflight'][-1]['observation'][v]['mergeStateStatus']=='CLEAN' for v in 'ABC')
last=x['queued_samples'][-1]['observation'];entries=last['mergeQueue']['entries']['nodes']
assert [v['pullRequest']['number'] for v in entries]==[case['prs']['A'],case['prs']['B']]
assert last['C']['isInMergeQueue'] is False
assert [v['number'] for v in x['queued_unstack']['data']['pull_requests']]==[case['prs']['A'],case['prs']['B']]
assert x['queued_unstack']['http']==200
initial=snap('queued-members-initial');after=snap('queued-members-after-queued-unstack');final=snap('queued-members-final')
assert after['prs']['C']['data'].get('stack') is None
for v in 'AB':assert after['prs'][v]['data']['stack']['number']==case['stack']
assert [v['id'] for v in entries]==[v['id'] for v in x['after_queued_unstack_graph']['mergeQueue']['entries']['nodes']]
assert not x['dequeue_response']['data'].get('errors')
assert x['queue_empty_after_A_dequeue'] is True
assert x['old_admission_uuid_after_dequeue']['data']['status']=='enqueued'
assert x['eligible_unstack']['http']==204 and final['stack']['http']==404
assert owned_refs(initial)==owned_refs(after)==owned_refs(final)
for v in 'ABC':
 for snapshot in [initial,after,final]:
  pr=snapshot['prs'][v]['data'];assert pr['state']=='open' and not pr['merged']
  assert pr['head']['sha']==case['heads'][v]['sha']
  assert pr['base']['ref']==initial['prs'][v]['data']['base']['ref']
 assert final['prs'][v]['data'].get('stack') is None
assert x['final_graph']['mergeQueue']['entries']['nodes']==[]
assert all(x['final_graph'][v]['isInMergeQueue'] is False for v in 'ABC')
group=read(P/'retained-queue-groups.json')[0];gc=group['commit']['data'];group_sha=group['sha']
assert [v['sha'] for v in gc['parents']]==[case['trunk_sha']]
a=read(E/'queued-members-A.commit.json');assert gc['tree']['sha']==a['tree']
assert group['statuses']['data']['state']=='pending' and group['statuses']['data']['statuses']==[]
assert any(c['name']=='queue-observe' and c['conclusion']=='success' for c in group['checks']['data']['check_runs'])
artifact=E/'actions-42544608573/queue-event-merge_group-42544608573-1'
context=read(artifact/'context.json');event=read(artifact/'event.json')
assert context['decision']=='success' and context['head']==group_sha and event['action']=='checks_requested'
assert context['env']['GITHUB_EVENT_NAME']=='merge_group'
assert context['env']['GITHUB_SHA']==event['merge_group']['head_sha']==group_sha
assert context['tree']==gc['tree']['sha']
assert not context['release_status']['posted_by_workflow']
assert "Agent-authored-by: AI agent acting on joshlf's behalf" in gc['message']
intents=list(E.glob('*.intent.json'));missing=[p.name for p in intents if not p.with_name(p.name.replace('.intent.json','.receipt.json')).exists()];assert not missing
result={'all_checks_passed':True,'prs':case['prs'],'stack_before':case['stack'],'ruleset_id':x['ruleset']['id'],'native_selected_prefix_queue_order_observed':[case['prs']['A'],case['prs']['B']],'unqueued_suffix_released_by_unstack':case['prs']['C'],'queued_members_retained_by_first_unstack':True,'queue_entry_ids_preserved_by_first_unstack':True,'dequeue_lower_removed_selected_and_dependent_upper':True,'old_uuid_after_dequeue':'enqueued','second_unstack_http':204,'final_group_get_http':404,'owned_refs_and_pr_bases_unchanged':True,'all_prs_open_unmerged_unstacked_unqueued':True,'queue_group_sha':group_sha,'queue_group_has_exact_lower_patch_tree':True,'actual_merge_group_event_and_successful_workflow_captured':True,'release_context_never_posted_to_group':True,'group_locally_retained_at':group['local_retained_ref'],'unresolved_api_intents':missing,'limitations':['Queued removal was tested after terminal admission, not cancellation of a still-pending background enqueue.','Only one small held native prefix; no universal provider handoff or no-delayed-write guarantee.','No group release or landing was attempted by this lane.']}
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
