#!/usr/bin/env python3
"""Read back final fixture identities, patches, receipts, and queue ownership."""
import hashlib,json,time
from pathlib import Path
import run
from lab import save,now,command
L=run.L;HOME=run.HOME

def digest(text):return hashlib.sha256(text.encode()).hexdigest()

def rawgit(*args):
    r=L.git(*args,check=False)
    if r.returncode:raise RuntimeError('Local Git audit failed: '+r.stderr)
    return r.stdout

def main():
    inputs=sorted((HOME/'cases').glob('*/state.json'))
    record={'start':now(),'scope':'only exp/fu2/queue fixtures','cases':{},'unresolved_intents':[]}
    fetch_args=['fetch','--no-tags','origin','+refs/heads/exp/fu2/queue/*:refs/remotes/origin/exp/fu2/queue/*','refs/tags/exp/fu2/queue/*:refs/tags/exp/fu2/queue/*']
    fetch={'start':now(),'args':fetch_args};save(HOME/'evidence/final-fetch-intent.json',fetch)
    result=L.git(*fetch_args,check=False);fetch.update({'end':now(),'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr});save(HOME/'evidence/final-fetch-receipt.json',fetch)
    assert result.returncode==0
    for path in inputs:
        s=json.loads(path.read_text());c=s['case'];o=run.observe(s,'final-audit',True)
        case={'start':o['start'],'end':o['end'],'queue':o['entries'],'phases':s['phases'],'prs':{},'receipts':{}}
        for label,a in s.get('admissions',{}).items():
            uuid=(a['receipt'].get('data') or {}).get('details',{}).get('uuid')
            if uuid:
                receipt=L.api(s['name']+'-'+label+'-final-uuid','GET',run.API+'/pulls/'+str(c['prs'][a['key']])+'/merge-async/'+uuid,fresh=True)
                case['receipts'][label]={'uuid':uuid,'selected_head':a['selected_head'],'final':receipt['data'],'evidence':receipt['label']}
        for k,h in c['heads'].items():
            original=h['sha'];ref='refs/remotes/origin/'+h['ref'];hosted=L.git('rev-parse',ref);archive=L.git('rev-parse','refs/tags/'+c['prefix']+'/authored/'+k+'/v1')
            oldparent=L.git('rev-parse',original+'^');newparent=L.git('rev-parse',hosted+'^')
            oldpatch=rawgit('diff','--binary',oldparent,original);newpatch=rawgit('diff','--binary',newparent,hosted)
            oldmeta=rawgit('show','-s','--format=%an%n%ae%n%aI%n%B',original);newmeta=rawgit('show','-s','--format=%an%n%ae%n%aI%n%B',hosted)
            case['prs'][k]={'number':c['prs'][k],'original_head':original,'git_ref_head':hosted,'graphql_head':o['prs'][k]['headRefOid'],'graphql_matches_git':hosted==o['prs'][k]['headRefOid'],'archive':archive,'archive_exact':archive==original,'source_rewritten':hosted!=original,'old_parent':oldparent,'new_parent':newparent,'patch_sha256':digest(oldpatch),'new_patch_sha256':digest(newpatch),'patch_preserved':oldpatch==newpatch,'author_date_message_preserved':oldmeta==newmeta,'lifecycle':o['prs'][k]}
        record['cases'][s['name']]=case;save(HOME/'FINAL-AUDIT.json',record)
    for p in (HOME/'evidence').glob('*.intent.json'):
        if not p.with_name(p.name.replace('.intent.json','.receipt.json')).exists():record['unresolved_intents'].append(str(p.relative_to(HOME)))
    for p in (HOME/'evidence').glob('*.push-intent.json'):
        if not p.with_name(p.name.replace('.push-intent.json','.push.json')).exists():record['unresolved_intents'].append(str(p.relative_to(HOME)))
    allruns=[]
    for page in range(1,6):
        data=run.good(L.api('final-all-actions-page-'+str(page),'GET',run.API+'/actions/runs?per_page=100&page='+str(page),fresh=True));allruns.extend(data['workflow_runs'])
        if len(data['workflow_runs'])<100:break
    else:raise RuntimeError('Final run pagination bound')
    own=[r for r in allruns if r['head_branch'].startswith(('exp/fu2/queue/','gh-readonly-queue/exp/fu2/queue/'))]
    by_name={json.loads(p.read_text())['case']['prefix']:p.parent for p in inputs}
    record['artifact_downloads']=[]
    for r in own:
        prefix=next((p for p in by_name if r['head_branch'].startswith(p+'/') or r['head_branch'].startswith('gh-readonly-queue/'+p+'/trunk/')),None)
        if prefix is None:raise RuntimeError('Run not bound to an owned fixture')
        folder=by_name[prefix]/'actions'/str(r['id'])
        if r['status']=='completed' and not folder.exists():
            folder.mkdir(parents=True);start=now()
            d=command(['gh','run','download',str(r['id']),'--repo',run.REPO,'--dir',str(folder)])
            download={'start':start,'end':now(),'id':r['id'],'exit':d.returncode,'stdout':d.stdout,'stderr':d.stderr};record['artifact_downloads'].append(download)
            save(folder.parent/(str(r['id'])+'-final-download.json'),download)
            if d.returncode:raise RuntimeError('Completed artifact download failed')
            run.good(L.api('final-jobs-'+str(r['id']),'GET',run.API+'/actions/runs/'+str(r['id'])+'/jobs',fresh=True))
    record['actions']=[{k:r[k] for k in ['id','event','head_branch','head_sha','status','conclusion']} for r in own]
    record['incomplete_actions']=[x for x in record['actions'] if x['status']!='completed']
    record['queue_empty']=all(not c['queue'] for c in record['cases'].values())
    record['archive_exact']=all(p['archive_exact'] for c in record['cases'].values() for p in c['prs'].values())
    record['patches_preserved']=all(p['patch_preserved'] for c in record['cases'].values() for p in c['prs'].values())
    record['graphql_git_coherent']=all(p['graphql_matches_git'] for c in record['cases'].values() for p in c['prs'].values())
    record['end']=now();save(HOME/'FINAL-AUDIT.json',record)
    print(json.dumps({k:record[k] for k in ['queue_empty','archive_exact','patches_preserved','graphql_git_coherent','unresolved_intents','incomplete_actions']},indent=2))
if __name__=='__main__':main()
