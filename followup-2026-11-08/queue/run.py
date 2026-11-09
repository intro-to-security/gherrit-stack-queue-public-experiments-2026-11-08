#!/usr/bin/env python3
"""Bounded synthetic queue cases; intents and receipts are authoritative records."""
import argparse, hashlib, json, time, traceback
from pathlib import Path
from urllib.parse import quote
from lab import Lane, REPO, save, now
L=Lane('queue'); HOME=L.home; API='repos/'+REPO
QFIELDS='id position state enqueuedAt headCommit{oid} baseCommit{oid} pullRequest{id number headRefOid}'

def good(r, codes=(200,)):
    if r['http'] not in codes or r.get('parse_error') or (isinstance(r.get('data'),dict) and r['data'].get('errors')):
        raise RuntimeError('Known API failure: '+r['label']+' '+str(r.get('data')))
    return r['data']

def state(name):
    p=HOME/'cases'/name/'state.json';p.parent.mkdir(parents=True,exist_ok=True)
    return json.loads(p.read_text()) if p.exists() else {'name':name,'observations':[],'phases':{}}

def store(s):save(HOME/'cases'/s['name']/'state.json',s)

def graph(c,label):
    prs=list(c['prs'].items())
    declarations=','.join('$p'+str(i)+':Int!' for i in range(len(prs)))
    blocks=' '.join('p'+str(i)+':pullRequest(number:$p'+str(i)+'){id number state merged mergedAt headRefOid baseRefOid baseRefName mergeStateStatus isInMergeQueue mergeQueueEntry{'+QFIELDS+'} timelineItems(last:20){nodes{__typename ... on RemovedFromMergeQueueEvent {createdAt reason beforeCommit{oid}} ... on MergedEvent {createdAt commit{oid}}}}}' for i in range(len(prs)))
    query='query($owner:String!,$repo:String!,$branch:String!,'+declarations+'){repository(owner:$owner,name:$repo){mergeQueue(branch:$branch){id entries(first:100){pageInfo{hasNextPage} nodes{'+QFIELDS+'}}} '+blocks+'}}'
    owner,repo=REPO.split('/');v={'owner':owner,'repo':repo,'branch':c['trunk'],**{'p'+str(i):n for i,(_,n) in enumerate(prs)}}
    r=L.graphql(label,query,v,fresh=True);data=good(r)['data']['repository']
    q=data.pop('mergeQueue');nodes=q['entries']['nodes'] if q else []
    if q: assert not q['entries']['pageInfo']['hasNextPage']
    return {'start':r['start'],'end':r['end'],'receipt':r['label'],'entries':nodes,'prs':{k:data['p'+str(i)] for i,(k,_) in enumerate(prs)}}

def observe(s,label,refs=False):
    o=graph(s['case'],s['name']+'-'+label)
    if refs:
        c=s['case'];o['refs_start']=now();o['refs']=L.git('ls-remote','origin','refs/heads/'+c['prefix']+'/*','refs/tags/'+c['prefix']+'/*','refs/heads/gh-readonly-queue/'+c['trunk']+'/*');o['refs_end']=now()
    s['observations'].append(o);store(s);return o

def rule(s,method='MERGE',strategy='ALLGREEN',build=1,maximum=5,hold=False,minimum=1,wait=1):
    c=s['case'];checks=[{'context':'queue-observe','integration_id':15368}]
    if hold: checks.append({'context':'experiment/queue-release'})
    body={'name':'gherrit-fu2-queue-'+s['name'],'target':'branch','enforcement':'active','bypass_actors':[], 'conditions':{'ref_name':{'include':['refs/heads/'+c['trunk']],'exclude':[]}},'rules':[{'type':'merge_queue','parameters':{'check_response_timeout_minutes':5,'grouping_strategy':strategy,'max_entries_to_build':build,'max_entries_to_merge':maximum,'merge_method':method,'min_entries_to_merge':minimum,'min_entries_to_merge_wait_minutes':wait}},{'type':'required_status_checks','parameters':{'strict_required_status_checks_policy':False,'required_status_checks':checks}}]}
    r=good(L.api(s['name']+'-create-rule','POST',API+'/rulesets',body),(201,));s['rule']=good(L.api(s['name']+'-rule-readback','GET',API+'/rulesets/'+str(r['id']),fresh=True));s['hold']=hold;store(s)
    if hold:
        for k,h in c['heads'].items(): good(L.status(s['name']+'-source-gate-'+k,h['sha'],'success'),(201,))

def setup(name,count=2,**settings):
    s=state(name)
    if 'case' not in s:s['case']=L.fixture(name,count=count,native=True);store(s)
    if 'rule' not in s:rule(s,**settings)
    s['phases']['setup']='complete';store(s);return s

def ready(s,keys=None,seconds=150):
    keys=keys or list(s['case']['prs']);deadline=time.monotonic()+seconds
    while True:
        o=observe(s,'ready')
        if all(o['prs'][k]['mergeStateStatus']=='CLEAN' for k in keys):s['source_clean']=o;store(s);return o
        if time.monotonic()>=deadline:raise RuntimeError('Source readiness bound; no admission sent')
        time.sleep(5)

def enqueue(s,key,label,immediate=None):
    c=s['case'];before=observe(s,label+'-before',True);head=before['prs'][key]['headRefOid']
    if before['prs'][key]['state']!='OPEN':raise RuntimeError('Selected PR is not open')
    payload={'sha':head,'merge_action':'merge_queue'}
    r=L.api(s['name']+'-'+label,'PUT',API+'/pulls/'+str(c['prs'][key])+'/merge-async',payload)
    s.setdefault('admissions',{})[label]={'key':key,'selected_head':head,'receipt':r};store(s)
    if immediate:
        dq=dequeue(s,immediate,label+'-immediate-'+immediate,before)
        s['admissions'][label]['immediate_dequeue']=dq;store(s)
    if r['http'] not in (200,202,409):return r
    uuid=(r.get('data') or {}).get('details',{}).get('uuid')
    if uuid:
        deadline=time.monotonic()+45
        while True:
            poll=L.api(s['name']+'-'+label+'-poll','GET',API+'/pulls/'+str(c['prs'][key])+'/merge-async/'+uuid,fresh=True)
            s['admissions'][label].setdefault('polls',[]).append(poll);store(s)
            if good(poll).get('status')!='pending' or time.monotonic()>=deadline:break
            time.sleep(2)
    observe(s,label+'-after',True);return r

def dequeue(s,key,label,before=None):
    before=before or observe(s,label+'-before');node=before['prs'][key]['id']
    query='mutation($id:ID!,$receipt:String!){dequeuePullRequest(input:{id:$id,clientMutationId:$receipt}){clientMutationId mergeQueueEntry{id position state pullRequest{id number}}}}'
    r=L.graphql(s['name']+'-'+label,query,{'id':node,'receipt':s['name']+'-'+label});s.setdefault('dequeues',{})[label]=r;store(s);return r

def wait_entries(s,keys,seconds=45):
    target=[s['case']['prs'][k] for k in keys];deadline=time.monotonic()+seconds
    while True:
        o=observe(s,'membership')
        if [e['pullRequest']['number'] for e in o['entries']]==target:return o
        if time.monotonic()>=deadline:raise RuntimeError('Membership bound: '+str(target))
        time.sleep(3)

def cleanup(s):
    o=observe(s,'cleanup-before')
    for i in range(len(s['case']['prs'])+1):
        if not o['entries']:s['cleanup']={'at':now(),'empty_observation':o};store(s);return
        e=min(o['entries'],key=lambda x:x['position']);keys=[k for k,n in s['case']['prs'].items() if n==e['pullRequest']['number']];assert len(keys)==1
        r=dequeue(s,keys[0],'cleanup-'+str(i),o)
        if (r.get('data') or {}).get('errors'):
            s['cleanup']={'at':now(),'blocked_by':r};store(s);return
        time.sleep(2);o=observe(s,'cleanup-after-'+str(i),True)
    raise RuntimeError('Explicit cleanup bound')

def capture(s):
    c=s['case'];o=observe(s,'capture',True)
    for label,admission in s.get('admissions',{}).items():
        uuid=(admission['receipt'].get('data') or {}).get('details',{}).get('uuid')
        if uuid:
            admission['post_outcome_receipt']=L.api(s['name']+'-'+label+'-post-outcome','GET',API+'/pulls/'+str(c['prs'][admission['key']])+'/merge-async/'+uuid,fresh=True)
    store(s)
    allruns=[]
    for page in range(1,6):
        r=good(L.api(s['name']+'-runs-page-'+str(page),'GET',API+'/actions/runs?per_page=100&page='+str(page),fresh=True))
        allruns.extend(r['workflow_runs'])
        if len(r['workflow_runs'])<100:break
    else:raise RuntimeError('Actions pagination bound reached')
    ownrefs={h['ref'] for h in c['heads'].values()};prefix='gh-readonly-queue/'+c['trunk']+'/'
    runs=[x for x in allruns if x['head_branch'] in ownrefs or (x['event']=='merge_group' and x['head_branch'].startswith(prefix))]
    s['runs']=runs
    for run in runs:
        rid=run['id'];good(L.api(s['name']+'-jobs-'+str(rid),'GET',API+'/actions/runs/'+str(rid)+'/jobs',fresh=True))
        folder=HOME/'cases'/s['name']/'actions'/str(rid)
        if run['status']=='completed' and not folder.exists():
            folder.mkdir(parents=True);start=now();r=L.git('rev-parse','HEAD',check=False)
            from lab import command
            d=command(['gh','run','download',str(rid),'--repo',REPO,'--dir',str(folder)])
            save(folder.parent/(str(rid)+'-download.json'),{'start':start,'end':now(),'exit':d.returncode,'stdout':d.stdout,'stderr':d.stderr})
    s['phases']['capture']='complete';store(s)

def candidates(s,seconds=90):
    deadline=time.monotonic()+seconds
    while True:
        o=observe(s,'candidates',True)
        entries=o['entries'];heads=[e['headCommit']['oid'] for e in entries if e.get('headCommit')]
        if entries and len(heads)==len(entries):return o
        if time.monotonic()>=deadline:return o
        time.sleep(4)

def check_candidates(s,o):
    rows={}
    for e in o['entries']:
        if e.get('headCommit'):
            sha=e['headCommit']['oid'];r=good(L.api(s['name']+'-candidate-checks-'+sha,'GET',API+'/commits/'+sha+'/check-runs',fresh=True));rows[sha]=r
    s.setdefault('candidate_checks',[]).append({'at':now(),'checks':rows});store(s);return rows

def release(s,keys=None,status='success',seconds=150):
    keys=keys or list(s['case']['prs']);deadline=time.monotonic()+seconds;sent=set(s.get('released',[]))
    while True:
        o=observe(s,'release-observe',True)
        for e in o['entries']:
            n=e['pullRequest']['number'];k=next(k for k,v in s['case']['prs'].items() if v==n)
            if k not in keys or not e.get('headCommit'):continue
            sha=e['headCommit']['oid']
            if sha in sent:continue
            checks=good(L.api(s['name']+'-release-check-'+sha,'GET',API+'/commits/'+sha+'/check-runs',fresh=True))
            if any(x['name']=='queue-observe' and x['conclusion']=='success' for x in checks['check_runs']):
                good(L.status(s['name']+'-release-'+sha,sha,status),(201,));sent.add(sha);s['released']=list(sent);store(s)
        if not o['entries'] or time.monotonic()>=deadline:return o
        time.sleep(4)

def watch(s,seconds=180):
    deadline=time.monotonic()+seconds
    while True:
        o=observe(s,'watch',True)
        if not o['entries']:return o
        if time.monotonic()>=deadline:return o
        time.sleep(4)

def removals():
    s=setup('q01-removals',3,hold=True);ready(s);enqueue(s,'C','admit-C');wait_entries(s,list('ABC'))
    for k in 'CBA':
        before=observe(s,'confirmed-before-'+k,True);s.setdefault('removal_preconditions',{})[k]=before;store(s)
        if before['prs'][k]['isInMergeQueue']:
            dequeue(s,k,'confirmed-dequeue-'+k,before);time.sleep(2);observe(s,'confirmed-after-'+k,True)
    cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def pending():
    s=setup('q02-pending-lower',2,hold=True);ready(s);enqueue(s,'B','admit-B',immediate='A');watch(s,12);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def matrix_setup():
    for method in ['MERGE','SQUASH','REBASE']:
        for strategy,build in [('HEADGREEN',1),('ALLGREEN',2),('HEADGREEN',2)]:setup('q03-'+method.lower()+'-'+strategy.lower()+'-'+str(build),method=method,strategy=strategy,build=build)

def matrix_run(method):
    names=['q03-'+method.lower()+'-'+strategy.lower()+'-'+str(build) for strategy,build in [('HEADGREEN',1),('ALLGREEN',2),('HEADGREEN',2)]]
    for name in names:
        s=state(name);ready(s);enqueue(s,'B','admit-B')
    for name in names:
        s=state(name);watch(s);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def size_setup():
    for n in [2,3,4]:setup('q04-size-'+str(n),n,build=4,maximum=2,hold=True)

def size_run():
    for n in [2,3,4]:
        s=state('q04-size-'+str(n));ready(s);enqueue(s,'ABCDE'[n-1],'admit-top');candidates(s);release(s);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def prefix():
    s=setup('q05-prefix',3,build=2,hold=True);ready(s);enqueue(s,'B','admit-B');wait_entries(s,['A','B']);release(s,['A','B']);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def failures():
    for strategy in ['ALLGREEN','HEADGREEN']:
        s=setup('q06-'+strategy.lower(),3,build=3,strategy=strategy,hold=True,minimum=3,wait=5);ready(s);enqueue(s,'C','admit-C');o=candidates(s)
        deadline=time.monotonic()+100
        while True:
            checks=check_candidates(s,o)
            if len(checks)==3 and all(any(x['name']=='queue-observe' and x['conclusion']=='success' for x in r['check_runs']) for r in checks.values()):break
            if time.monotonic()>=deadline:raise RuntimeError('Real candidate Actions not successful at bound')
            time.sleep(4);o=observe(s,'failure-ready')
        for k,status in [('A','success'),('C','success'),('B','failure')]:
            e=next(x for x in o['entries'] if x['pullRequest']['number']==s['case']['prs'][k]);sha=e['headCommit']['oid'];good(L.status(s['name']+'-candidate-'+k+'-'+status,sha,status),(201,))
        watch(s,45);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def advance(conflict):
    name='q08-'+('conflict' if conflict else 'clear');s=state(name)
    if 'case' not in s:s['case']=L.fixture(name,count=2,native=True);store(s)
    c=s['case'];files={name+'/A.txt':'A=trunk-conflict\n'} if conflict else {name+'/advanced.txt':'advanced trunk\n'}
    sha=L.commit(name+'-advance',c['trunk_sha'],files)
    goodpush=L.push(name+'-advance',{'refs/heads/'+c['trunk']:sha},{'refs/heads/'+c['trunk']:c['trunk_sha']});assert goodpush['exit']==0
    s['advanced_trunk']=sha;store(s)
    if 'rule' not in s:rule(s)
    if conflict:
        advance_clean(name);return
    time.sleep(5);observe(s,'advanced-before');enqueue(s,'B','advanced-admission');watch(s,10);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def readmit():
    s=setup('q09-readmit',2,method='SQUASH');ready(s);enqueue(s,'B','first-admit-B');watch(s)
    deadline=time.monotonic()+120
    while True:
        o=observe(s,'new-head-readiness',True);b=o['prs']['B']
        if b['merged']:s['readmission_unavailable']='Original request already merged B';store(s);break
        if not o['entries'] and b['headRefOid']!=s['case']['heads']['B']['sha'] and b['mergeStateStatus']=='CLEAN':enqueue(s,'B','explicit-new-head-admit');watch(s);break
        if time.monotonic()>=deadline:s['readmission_unavailable']='No new CLEAN unqueued head observed within bound';store(s);break
        time.sleep(4)
    cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def independent():
    name='q07-independent';s=state(name)
    if 'case' not in s:
        c=L.fixture(name,2,native=True);s['case']=c;store(s)
        for k,parent in [('X',c['trunk_sha']),('C',c['trunk_sha']),('D',None)]:
            parent=parent or c['heads']['C']['sha'];sha=L.commit(name+'-'+k,parent,{name+'/'+k+'.txt':k+'=1\n'});ref=c['prefix']+'/'+k
            assert L.push(name+'-initial-'+k,{'refs/heads/'+ref:sha,'refs/tags/'+c['prefix']+'/authored/'+k+'/v1':sha})['exit']==0
            base=c['heads']['C']['ref'] if k=='D' else c['trunk']
            p=good(L.api(name+'-create-'+k,'POST',API+'/pulls',{'head':ref,'base':base,'title':'Synthetic queue experiment '+name+': '+k,'body':'Independent synthetic queue work.\n\n'+__import__('lab').NOTICE}),(201,))
            c['heads'][k]={'ref':ref,'sha':sha};c['prs'][k]=p['number'];L.save_fixture(c);s['case']=c;store(s)
        stack=good(L.api(name+'-register-CD','POST',API+'/stacks',{'pull_requests':[c['prs']['C'],c['prs']['D']]}),(201,));s['second_stack']=stack['number'];store(s)
    if 'rule' not in s:rule(s,build=3,hold=True)
    ready(s)
    for k in 'XBD':enqueue(s,k,'admit-'+k)
    before=wait_entries(s,list('XABCD'));dequeue(s,'A','remove-A-with-independent',before);time.sleep(3);observe(s,'after-remove-A',True);cleanup(s);capture(s);s['phases']['run']='complete';store(s)

def advance_clean(name):
    s=state(name)
    deadline=time.monotonic()+150
    while True:
        o=observe(s,'advanced-check-control',True);rows={}
        for k,h in s['case']['heads'].items():
            rows[k]=good(L.api(name+'-source-check-'+k,'GET',API+'/commits/'+h['sha']+'/check-runs',fresh=True))
        s['advanced_check_control']=rows;store(s)
        if all(any(x['name']=='queue-observe' and x['conclusion']=='success' for x in r['check_runs']) for r in rows.values()):break
        if time.monotonic()>=deadline:raise RuntimeError('Advanced-trunk source check bound')
        time.sleep(5)
    enqueue(s,'B','checks-clean-admission');watch(s);cleanup(s);capture(s);s['phases']['clean_control']='complete';store(s)


def occupied(n):
    name='q04-occupied-'+str(n);s=state(name)
    if 'case' not in s:
        c=L.fixture(name,n,native=True);s['case']=c;store(s)
        sha=L.commit(name+'-X',c['trunk_sha'],{name+'/X.txt':'independent=1\n'});ref=c['prefix']+'/X'
        assert L.push(name+'-initial-X',{'refs/heads/'+ref:sha,'refs/tags/'+c['prefix']+'/authored/X/v1':sha})['exit']==0
        p=good(L.api(name+'-create-X','POST',API+'/pulls',{'head':ref,'base':c['trunk'],'title':'Synthetic queue experiment '+name+': independent X','body':'Synthetic occupied-queue boundary control.\n\n'+__import__('lab').NOTICE}),(201,))
        c['heads']['X']={'ref':ref,'sha':sha};c['prs']['X']=p['number'];L.save_fixture(c);s['case']=c;store(s)
    if 'rule' not in s:rule(s,build=4,maximum=2,minimum=2,wait=5,hold=True)
    ready(s);enqueue(s,'X','admit-X');enqueue(s,'ABCDE'[n-1],'admit-top');o=candidates(s)
    deadline=time.monotonic()+100
    while True:
        checks=check_candidates(s,o)
        if len(checks)==n+1 and all(any(x['name']=='queue-observe' and x['conclusion']=='success' for x in r['check_runs']) for r in checks.values()):break
        if time.monotonic()>=deadline:raise RuntimeError('Occupied boundary candidate checks bound')
        time.sleep(4);o=observe(s,'occupied-ready',True)
    for k in list(reversed('ABCDE'[:n]))+['X']:
        e=next(x for x in o['entries'] if x['pullRequest']['number']==s['case']['prs'][k]);sha=e['headCommit']['oid'];good(L.status(name+'-ordered-release-'+k,sha,'success'),(201,))
    watch(s);cleanup(s);capture(s);s['phases']['run']='complete';store(s)


def main():
    p=argparse.ArgumentParser();p.add_argument('op');p.add_argument('arg',nargs='?');a=p.parse_args()
    save(HOME/('source-'+str(time.time_ns())+'.json'),{'at':now(),'run_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'lab_sha256':hashlib.sha256((HOME/'lab.py').read_bytes()).hexdigest()})
    {'occupied':lambda:occupied(int(a.arg)),'removals':removals,'pending':pending,'matrix-setup':matrix_setup,'matrix-run':lambda:matrix_run(a.arg),'size-setup':size_setup,'size-run':size_run,'prefix':prefix,'failures':failures,'independent':independent,'advance-clear':lambda:advance(False),'advance-conflict':lambda:advance(True),'readmit':readmit,'advance-clean-control':lambda:advance_clean(a.arg),'capture':lambda:capture(state(a.arg)),'cleanup':lambda:cleanup(state(a.arg))}[a.op]()
if __name__=='__main__':
    try:main()
    except Exception:
        p=HOME/('failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc());print('STOPPED '+str(p),flush=True);raise
