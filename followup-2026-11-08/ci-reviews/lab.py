#!/usr/bin/env python3
"""Bounded follow-up fixtures with durable dispatch records and readbacks."""
import base64, datetime, json, os, pathlib, subprocess, sys, time, urllib.parse
HERE=pathlib.Path(__file__).resolve().parent
REPO='joshlf/gherrit-native-stack-experiments-2026-11-08'; R='repos/'+REPO
CO=HERE/'repo'; EV=HERE/'evidence'; CT=HERE/'control'; ST=HERE/'state.json'
NOTICE="*Authored by an AI agent acting on joshlf's behalf.*"
TRAILER="Agent-authored-by: AI agent acting on joshlf's behalf"
SIGNED1='7ca2b1a7a38f3b3f6f1325c121bb11b025a1c786'; SIGNED2='7c586aee5324ed0aed0a97c310fdab00e025b27c'; SIGNEDBASE='d6223f27f364a74460a907df8087d3c52331ca3d'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def load():return json.loads(ST.read_text()) if ST.exists() else {'repo':REPO}
def save(s):
    pending=ST.with_name(ST.name+'.'+str(os.getpid())+'.pending');write(pending,s);os.replace(pending,ST)
def run(label,args,data=None,cwd=HERE,ok=(0,)):
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); stem=EV/(stamp+'-'+label)
    record={'at':now(),'argv':args,'cwd':str(cwd)}
    if data is not None:stem.with_suffix('.request').write_text(data);record['request']=str(stem.with_suffix('.request').relative_to(HERE))
    if 'push' in args or '--method' in args and args[args.index('--method')+1]!='GET':write(CT/(stamp+'-'+label+'-intent.json'),record)
    p=subprocess.run(args,input=data,text=True,capture_output=True,cwd=cwd,env={**os.environ,'XDG_CACHE_HOME':str(HERE/'.cache')})
    stem.with_suffix('.stdout').write_text(p.stdout);stem.with_suffix('.stderr').write_text(p.stderr)
    record.update(finished=now(),returncode=p.returncode,stdout=str(stem.with_suffix('.stdout').relative_to(HERE)),stderr=str(stem.with_suffix('.stderr').relative_to(HERE)))
    with (EV/'commands.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
    if p.returncode not in ok:raise RuntimeError(label+': '+p.stderr)
    return p.stdout
def api(label,path,method='GET',body=None,ok=(0,)):
    args=['gh','api','--method',method,path]
    if body is not None:args+=['--input','-']
    raw=run(label,args,json.dumps(body) if body is not None else None,ok=ok)
    try:return json.loads(raw)
    except json.JSONDecodeError:return raw

def git(label,*args,ok=(0,)):
    return run(label,['git','-c','core.hooksPath=/dev/null',*args],cwd=CO,ok=ok).strip()
def commit(label,file,text):
    p=CO/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    git(label+'-add','add','--',file)
    git(label+'-commit','-c','user.name=Josh Liebow-Feeser','-c','user.email=hello@joshlf.com','-c','commit.gpgsign=false','commit','-m','Record '+label+' synthetic fixture','-m',TRAILER)
    return git(label+'-sha','rev-parse','HEAD')
def create(key,bot=False,mode='unsigned',target=False,owners=False,codeql=False,push_ci=False):
    s=load();assert key not in s,'Reconcile existing fixture instead of repeating'
    stem='exp/fu2/ci/'+key;c={x:stem+'/'+x for x in ['trunk','lower','upper']};c.update(bot=bot,mode=mode)
    seed=git(key+'-seed','rev-parse','origin/main') if mode=='unsigned' else SIGNEDBASE
    c['seed']=seed;git(key+'-trunk','checkout','-b',c['trunk'],seed)
    if owners:commit(key+'-owners','.github/CODEOWNERS','* @joshlf\n')
    if target:
        source=(CO/'.github/workflows/observe.yml').read_text();source=source.replace('name: observe','name: fu2-target').replace('  observe:','  fu2-target:').replace('  pull_request:\n    types: [opened, synchronize, reopened, ready_for_review]','  pull_request_target:\n    types: [opened, synchronize, stacked]\n    branches: [\'exp/fu2/ci/{key}/trunk\']')
        source=source.replace('{key}',key)
        assert 'pull_request_target:' in source
        commit(key+'-target','.github/workflows/observe.yml' if key=='target-knownpath' else '.github/workflows/fu2-target.yml',source)
    if codeql:
        commit(key+'-python','fu2_scanning_fixture.py','def add(left, right):\n    return left + right\n')
        workflow="""name: fu2-codeql
on:
  push:
    branches: ['exp/fu2/ci/scan-codeql/trunk']
  pull_request:
    types: [opened, synchronize, stacked]
    branches: ['exp/fu2/ci/scan-codeql/trunk']
permissions:
  contents: read
  security-events: write
  actions: read
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - uses: github/codeql-action/init@9418214df1f2c4b8128c770156c409013b07d6b9
        with:
          languages: python
      - uses: github/codeql-action/analyze@9418214df1f2c4b8128c770156c409013b07d6b9
        with:
          category: fu2-python
"""
        commit(key+'-workflow','.github/workflows/fu2-codeql.yml',workflow)
    if push_ci:
        source=(CO/'.github/workflows/observe.yml').read_text().split('permissions:',1)[1]
        source="name: fu2-push\non:\n  push:\n    branches: ['exp/fu2/ci/push/*']\npermissions:"+source
        source=source.replace('  observe:','  fu2-push:')
        commit(key+'-push-workflow','.github/workflows/fu2-push.yml',source)
    c['trunk_sha']=git(key+'-trunk-sha','rev-parse','HEAD')
    git(key+'-lower','checkout','-b',c['lower'])
    if mode in ['signed','signedmulti','mixedmulti','mixedsuffix']:
        git(key+'-signed-lower','reset','--hard',SIGNED2 if mode=='signedmulti' else SIGNED1)
    else:
        commit(key+'-lower','fu2-'+key+'-lower.txt','Synthetic lower layer.\n')
    if mode=='unsignedmulti':commit(key+'-lower2','fu2-'+key+'-lower2.txt','Synthetic lower second commit.\n')
    if mode=='mixedmulti':commit(key+'-mixedlower','fu2-'+key+'-lower2.txt','Unsigned second commit after verified source.\n')
    c['lower_sha']=git(key+'-lower-sha','rev-parse','HEAD')
    git(key+'-upper','checkout','-b',c['upper'])
    if mode in ['signed','mixedsuffix']:git(key+'-signed-upper','reset','--hard',SIGNED2)
    if mode!='signed':commit(key+'-upper','fu2-'+key+'-upper.txt','Synthetic upper layer.\n')
    c['upper_sha']=git(key+'-upper-sha','rev-parse','HEAD');s[key]=c;save(s)
    git(key+'-push','push','--atomic','origin',c['trunk'],c['lower'],c['upper'])
    if not bot:
        for pos,base in [('lower','trunk'),('upper','lower')]:
            pr=api(key+'-'+pos+'-create',R+'/pulls','POST',{'head':c[pos],'base':c[base],'title':'Follow-up CI '+key+': '+pos,'body':'Authorized synthetic follow-up fixture.\n\n'+NOTICE});c[pos+'_pr']=pr['number'];save(s)
    return c

def rule(key,context=None,reviews=False,lastpush=False,owners=False,signatures=False,admins=True,deploy=None):
    c=load()[key];p=R+'/branches/'+urllib.parse.quote(c['trunk'],safe='')+'/protection'
    body={'required_status_checks':{'strict':False,'contexts':[context]} if context else None,'enforce_admins':admins,'required_pull_request_reviews':{'dismiss_stale_reviews':True,'require_code_owner_reviews':owners,'required_approving_review_count':1,'require_last_push_approval':lastpush} if reviews else None,'restrictions':None}
    api(key+'-protect',p,'PUT',body)
    if signatures:api(key+'-signature-rule',p+'/required_signatures','POST')
    if deploy:api(key+'-deployment-rule',p+'/required_deployments','POST',{'environments':[deploy]})
    return api(key+'-protect-readback',p)

def dispatch(key,op='create-pr',position=None):
    c=load()[key]
    for pos,base in ([('lower','trunk'),('upper','lower')] if position is None else [(position,'trunk')]):
        inputs={'operation':op,'head':c[pos],'base':c[base],'title':'Follow-up review '+key+': '+pos,'body':'Synthetic distinct-author review fixture.\n\n'+NOTICE}
        if op=='approve-pr':inputs={'operation':op,'number':str(c[pos+'_pr'])}
        api(key+'-'+pos+'-dispatch',R+'/actions/workflows/automation.yml/dispatches','POST',{'ref':'exp/fu2/ci/control/workflow','inputs':inputs})
def discover(key):
    s=load();c=s[key]
    for pos in ['lower','upper']:
        prs=api(key+'-'+pos+'-discover',R+'/pulls?state=open&head=joshlf:'+c[pos]);assert len(prs)==1
        assert prs[0]['user']['login']=='github-actions[bot]';c[pos+'_pr']=prs[0]['number']
    save(s);return c

def register(key):
    s=load();c=s[key];assert 'stack' not in c
    c['stack']=api(key+'-register',R+'/stacks','POST',{'pull_requests':[c['lower_pr'],c['upper_pr']]});save(s);return c['stack']
def approve(key):
    c=load()[key]
    for pos in ['lower','upper']:
        pr=api(key+'-'+pos+'-preapprove',R+'/pulls/'+str(c[pos+'_pr']));assert pr['user']['login']=='github-actions[bot]'
        api(key+'-'+pos+'-approve',R+'/pulls/'+str(c[pos+'_pr'])+'/reviews','POST',{'event':'APPROVE','commit_id':pr['head']['sha'],'body':'Synthetic machine-controlled approval only.\n\n'+NOTICE})

def snapshot(key,label):
    c=load()[key];out={'at':now(),'label':label}
    for pos in ['lower','upper']:
        n=c[pos+'_pr'];pr=api(key+'-'+label+'-'+pos,R+'/pulls/'+str(n));out[pos]=pr
        out[pos+'_graphql']=json.loads(run(key+'-'+label+'-'+pos+'-rollup',['gh','pr','view',str(n),'--repo',REPO,'--json','number,headRefOid,baseRefName,reviewDecision,mergeStateStatus,statusCheckRollup,latestReviews']))
        for res in ['reviews','commits'] :out[pos+'_'+res]=api(key+'-'+label+'-'+pos+'-'+res,R+'/pulls/'+str(n)+'/'+res)
        out[pos+'_timeline']=api(key+'-'+label+'-'+pos+'-timeline',R+'/issues/'+str(n)+'/timeline?per_page=100')
        for what,sha in [('head',pr['head']['sha']),('candidate',pr.get('merge_commit_sha'))]:
            if sha:
                out[pos+'_'+what+'_commit']=api(key+'-'+label+'-'+pos+'-'+what+'-commit',R+'/git/commits/'+sha,ok=(0,1))
                out[pos+'_'+what+'_checks']=api(key+'-'+label+'-'+pos+'-'+what+'-checks',R+'/commits/'+sha+'/check-runs?per_page=100')
                out[pos+'_'+what+'_status']=api(key+'-'+label+'-'+pos+'-'+what+'-status',R+'/commits/'+sha+'/status')
    out['protection']=api(key+'-'+label+'-protection',R+'/branches/'+urllib.parse.quote(c['trunk'],safe='')+'/protection',ok=(0,1))
    write(EV/('snapshot-'+key+'-'+label+'.json'),out)
    return {p:{'number':out[p]['number'],'head':out[p]['head']['sha'],'candidate':out[p].get('merge_commit_sha'),'review':out[p+'_graphql']['reviewDecision'],'gate':out[p+'_graphql']['mergeStateStatus']} for p in ['lower','upper']}

def advance(key):
    s=load();c=s[key];git(key+'-trunk-fetch','fetch','origin',c['trunk']);git(key+'-advance-checkout','checkout',c['trunk']);git(key+'-advance-reset','reset','--hard','origin/'+c['trunk'])
    c['advanced_trunk']=commit(key+'-advance','fu2-'+key+'-trunk.txt','Unrelated synthetic trunk advancement.\n');save(s)
    git(key+'-advance-push','push','origin',c['trunk']);return c['advanced_trunk']

def merge(key):
    s=load();c=s[key];assert 'merge_request' not in c
    pr=api(key+'-merge-preflight',R+'/pulls/'+str(c['lower_pr']))
    c['merge_request']=api(key+'-merge',R+'/pulls/'+str(c['lower_pr'])+'/merge-async','PUT',{'sha':pr['head']['sha'],'merge_method':'squash','merge_action':'default','bypass_rules':False});save(s);return c['merge_request']
def poll(key):
    c=load()[key];uuid=c['merge_request'].get('details',{}).get('uuid');assert uuid
    result=api(key+'-poll',R+'/pulls/'+str(c['lower_pr'])+'/merge-async/'+uuid);write(EV/(key+'-last-merge-receipt.json'),result);return result

def status(key,pos,state,candidate=False):
    c=load()[key];pr=api(key+'-status-preflight',R+'/pulls/'+str(c[pos+'_pr']));sha=pr['merge_commit_sha'] if candidate else pr['head']['sha']
    return api(key+'-'+pos+'-'+('candidate' if candidate else 'head')+'-'+state,R+'/statuses/'+sha,'POST',{'state':state,'context':'fu2-status','description':'Synthetic status-producer control'})

def collect(key):
    c=load()[key];out=[]
    for branch in [c['lower'],c['upper']]:
        runs=api(key+'-runs-'+branch.split('/')[-1],R+'/actions/runs?branch='+urllib.parse.quote(branch,safe='')+'&per_page=100')['workflow_runs']
        for r in runs:
            out.append({k:r[k] for k in ['id','event','name','head_sha','head_branch','status','conclusion','created_at']})
            if r['status']=='completed':
                dest=EV/'actions'/str(r['id'])
                if not dest.exists():run(key+'-download-'+str(r['id']),['gh','run','download',str(r['id']),'--repo',REPO,'--dir',str(dest)],ok=(0,1))
            api(key+'-jobs-'+str(r['id']),R+'/actions/runs/'+str(r['id'])+'/jobs')
    write(EV/(key+'-runs.json'),out);return out

if __name__=='__main__':
    cmd,*args=sys.argv[1:]
    if cmd=='init':
        git('origin','remote','set-url','origin','https://github.com/'+REPO+'.git');git('fetch','fetch','origin','main');print(api('baseline',R))
    elif cmd=='create':print(json.dumps(create(args[0],bot='bot' in args,mode=next((a for a in args[1:] if a not in ['bot','target','owners']),'unsigned'),target='target' in args,owners='owners' in args)))
    elif cmd=='snapshot':print(json.dumps(snapshot(*args),indent=2))
    elif cmd=='rule':print(json.dumps(rule(args[0],context='fu2-status' if 'status' in args else 'fu2-target' if 'target' in args else None,reviews='reviews' in args,lastpush='lastpush' in args,owners='owners' in args,signatures='signatures' in args,admins='noadmins' not in args)))
    elif cmd=='dispatch':dispatch(args[0],op='approve-pr' if 'approve' in args else 'create-pr',position='lower' if 'approve' in args else None)
    else:print(json.dumps(globals()[cmd](*args),indent=2))
