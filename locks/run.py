#!/usr/bin/env python3
import json,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from lab import Lane,REPO,save,now
L=Lane('locks');R='repos/'+REPO;HOME=L.home
RESULT=HOME/'results.json'
QUEUE_FIELDS='id position state enqueuedAt headCommit { oid } baseCommit { oid } pullRequest { id number headRefOid }'

def graph(case,label):
 query='''query($owner:String!,$repo:String!,$branch:String!,$a:Int!,$b:Int!,$c:Int!){repository(owner:$owner,name:$repo){
 mergeQueue(branch:$branch){id url entries(first:100){nodes{'''+QUEUE_FIELDS+'''} pageInfo{hasNextPage endCursor}}}
 A:pullRequest(number:$a){id number state merged mergedAt headRefOid baseRefName mergeStateStatus isInMergeQueue mergeQueueEntry{'''+QUEUE_FIELDS+'''}}
 B:pullRequest(number:$b){id number state merged mergedAt headRefOid baseRefName mergeStateStatus isInMergeQueue mergeQueueEntry{'''+QUEUE_FIELDS+'''}}
 C:pullRequest(number:$c){id number state merged mergedAt headRefOid baseRefName mergeStateStatus isInMergeQueue mergeQueueEntry{'''+QUEUE_FIELDS+'''}}
 }}'''
 owner,repo=REPO.split('/');variables={'owner':owner,'repo':repo,'branch':case['trunk'],**{x.lower():case['prs'][x] for x in 'ABC'}}
 receipt=L.graphql(label,query,variables,fresh=True)
 assert receipt['http']==200 and receipt['exit']==0 and not receipt['data'].get('errors'),receipt
 return receipt['data']['data']['repository']

def queue_numbers(observation):return [e['pullRequest']['number'] for e in observation['mergeQueue']['entries']['nodes']]
def assert_open(observation):assert all(observation[x]['state']=='OPEN' and not observation[x]['merged'] for x in 'ABC'),observation

def main():
 assert not RESULT.exists(),'Do not replay a completed queue fixture'
 case=L.fixture('queued-members',count=3,native=True)
 result={'case':case,'started':now(),'phase':'fixture-created'};save(RESULT,result)
 rules={'name':'locks-queued-members','target':'branch','enforcement':'active','bypass_actors':[],
 'conditions':{'ref_name':{'include':['refs/heads/'+case['trunk']],'exclude':[]}},
 'rules':[{'type':'merge_queue','parameters':{'check_response_timeout_minutes':5,'grouping_strategy':'ALLGREEN','max_entries_to_build':1,'max_entries_to_merge':3,'merge_method':'SQUASH','min_entries_to_merge':1,'min_entries_to_merge_wait_minutes':1}},
 {'type':'required_status_checks','parameters':{'required_status_checks':[{'context':'queue-observe'},{'context':'experiment/queue-release'}],'strict_required_status_checks_policy':False}}]}
 created=L.api('queued-members-ruleset','POST',R+'/rulesets',rules);assert created['http']==201,created
 result['ruleset']=created['data'];save(RESULT,result)
 for x in 'ABC':
  receipt=L.status('queued-members-pr-release-'+x,case['heads'][x]['sha'],'success');assert receipt['http']==201,receipt
 first=L.snapshot(case,'queued-members-initial')
 result['initial_snapshot']='evidence/queued-members-initial.snapshot.json';save(RESULT,result)
 deadline=time.monotonic()+90;preflight=[]
 while True:
  observed=graph(case,'queued-members-preflight-'+str(len(preflight)));preflight.append({'at':now(),'observation':observed})
  result['preflight']=preflight;save(RESULT,result)
  if all(observed[x]['mergeStateStatus']=='CLEAN' for x in 'AB'):break
  if time.monotonic()>=deadline:
   result['phase']='stopped-before-admission-required-checks-not-clean';save(RESULT,result);return
  time.sleep(4)
 selected=case['prs']['B'];payload={'sha':case['heads']['B']['sha'],'merge_action':'merge_queue','bypass_rules':False}
 request=L.api('queued-members-enqueue','PUT',R+'/pulls/'+str(selected)+'/merge-async',payload)
 result['admission_request']=request;save(RESULT,result);assert request['http'] in [200,202],request
 uuid=(request.get('data') or {}).get('details',{}).get('uuid');result['uuid']=uuid;save(RESULT,result)
 admission=request;polls=[];deadline=time.monotonic()+30
 while admission.get('data',{}).get('status')=='pending' and uuid and time.monotonic()<deadline:
  admission=L.api('queued-members-admission-poll-'+str(len(polls)),'GET',R+'/pulls/'+str(selected)+'/merge-async/'+uuid,fresh=True)
  polls.append(admission);result['admission_polls']=polls;save(RESULT,result)
  if admission.get('data',{}).get('status')=='pending':time.sleep(1)
 assert admission.get('data',{}).get('status')=='enqueued',admission
 result['admission_terminal']=admission;save(RESULT,result)
 deadline=time.monotonic()+35;queued_samples=[]
 while True:
  observed=graph(case,'queued-members-held-'+str(len(queued_samples)));assert_open(observed)
  queued_samples.append({'at':now(),'observation':observed});result['queued_samples']=queued_samples;save(RESULT,result)
  numbers=queue_numbers(observed)
  assert case['prs']['C'] not in numbers,observed
  if numbers==[case['prs']['A'],case['prs']['B']]:
   if any(e['headCommit'] is not None for e in observed['mergeQueue']['entries']['nodes']):break
  if time.monotonic()>=deadline:break
  time.sleep(3)
 assert queue_numbers(observed)==[case['prs']['A'],case['prs']['B']],observed
 result['group_heads_before_unstack']=[e['headCommit'] for e in observed['mergeQueue']['entries']['nodes']];save(RESULT,result)
 L.snapshot(case,'queued-members-before-unstack')
 unstack=L.api('queued-members-unstack-while-queued','POST',R+'/stacks/'+str(case['stack'])+'/unstack')
 result['queued_unstack']=unstack;save(RESULT,result)
 after_unstack=L.snapshot(case,'queued-members-after-queued-unstack');q_unstack=graph(case,'queued-members-queue-after-unstack');assert_open(q_unstack)
 result['after_queued_unstack_graph']=q_unstack;save(RESULT,result)
 assert unstack['http'] in [200,204],unstack
 a_node=q_unstack['A']['id']
 query='mutation($id:ID!,$receipt:String!){dequeuePullRequest(input:{id:$id,clientMutationId:$receipt}){clientMutationId mergeQueueEntry{id position state pullRequest{id number}}}}'
 dequeued=L.graphql('queued-members-dequeue-A',query,{'id':a_node,'receipt':'queued-members-dequeue-A'})
 result['dequeue_response']=dequeued;save(RESULT,result)
 assert dequeued['http']==200 and not dequeued['data'].get('errors'),dequeued
 deadline=time.monotonic()+30;removal=[]
 while True:
  observed=graph(case,'queued-members-after-dequeue-'+str(len(removal)));assert_open(observed)
  removal.append({'at':now(),'observation':observed});result['dequeue_observations']=removal;save(RESULT,result)
  if not queue_numbers(observed):break
  if time.monotonic()>=deadline:break
  time.sleep(2)
 result['queue_empty_after_A_dequeue']=not queue_numbers(observed);save(RESULT,result)
 if queue_numbers(observed):
  result['phase']='residual-queue-requires-explicit-reconciliation';save(RESULT,result);return
 if uuid:
  old=L.api('queued-members-old-uuid-after-dequeue','GET',R+'/pulls/'+str(selected)+'/merge-async/'+uuid,fresh=True)
  result['old_admission_uuid_after_dequeue']=old;save(RESULT,result)
 cleanup=L.api('queued-members-unstack-after-dequeue','POST',R+'/stacks/'+str(case['stack'])+'/unstack')
 result['eligible_unstack']=cleanup;save(RESULT,result)
 final=L.snapshot(case,'queued-members-final');finalq=graph(case,'queued-members-final-queue');assert_open(finalq)
 result['final_graph']=finalq;result['final_snapshot']='evidence/queued-members-final.snapshot.json';result['phase']='complete';result['finished']=now();save(RESULT,result)
 print(json.dumps({'prs':case['prs'],'stack':case['stack'],'uuid':uuid,'queued_unstack_http':unstack['http'],'queue_empty_after_A_dequeue':result['queue_empty_after_A_dequeue'],'eligible_unstack_http':cleanup['http'],'group_heads_before_unstack':result['group_heads_before_unstack'],'phase':result['phase']},indent=2))

if __name__=='__main__':main()
