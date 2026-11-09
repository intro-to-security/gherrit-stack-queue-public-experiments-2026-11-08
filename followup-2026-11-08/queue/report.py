#!/usr/bin/env python3
"""Build the case index from retained observations without inventing outcomes."""
import json
from pathlib import Path
from lab import save,now
HOME=Path(__file__).resolve().parent
PRIOR='experiments/native-stacks-2026-11-08/public-org-queue-2026-11-08/'

def main():
    audit=json.loads((HOME/'FINAL-AUDIT.json').read_text());rows=[]
    for path in sorted((HOME/'cases').glob('*/state.json')):
        s=json.loads(path.read_text());n=s['name'];final=audit['cases'][n];o=s['observations'][-1]
        rule=s.get('rule',{});parameters=next((r['parameters'] for r in rule.get('rules',[]) if r['type']=='merge_queue'),{})
        out={'id':n,'disposition':'performed','evidence':['queue/'+str(path.relative_to(HOME)),'queue/FINAL-AUDIT.json#cases/'+n],'prs':s['case']['prs'],'settings':parameters,'held_by_synthetic_gate':s.get('hold',False),'final_landed':[k for k,v in o['prs'].items() if v['merged']],'final_open':[k for k,v in o['prs'].items() if v['state']=='OPEN'],'removal_reasons':{k:[x['reason'] for x in v['timelineItems']['nodes'] if 'reason'in x] for k,v in o['prs'].items()},'final_queue_empty':not final['queue'],'admission_receipts':final['receipts'],'dequeue_outcomes':{label:r['data'] for label,r in s.get('dequeues',{}).items()},'source_rewritten':[k for k,p in final['prs'].items() if p['source_rewritten']],'raw_patches_preserved':all(p['patch_preserved'] for p in final['prs'].values()),'archives_exact':all(p['archive_exact'] for p in final['prs'].values())}
        if n=='q01-removals':
            for k in 'CBA':
                child=dict(out,id='Q01-'+k,question='Confirmed dequeue '+k,decisive_receipt='queue/evidence/'+n+'-confirmed-dequeue-'+k+'.receipt.json');rows.append(child)
        else:rows.append(out)
    for method,suffix,prs in [('MERGE','-merge',[28,29]),('SQUASH','',[25,26]),('REBASE','-rebase',[31,32])]:
        rows.append({'id':'Q03-'+method.lower()+'-allgreen-1','disposition':'reused','why':'Exact method/strategy/build/check control already executed in prior campaign; fresh remaining cells test new settings interactions.','settings':{'merge_method':method,'grouping_strategy':'ALLGREEN','max_entries_to_build':1,'max_entries_to_merge':5},'prs':prs,'outcome':'both landed' if method=='MERGE' else 'lower landed; upper invalid_merge_commit and native rewrite','evidence':[PRIOR+'ci/native-no-manual-gate'+suffix+'/RESULTS.md',PRIOR+'ci/native-no-manual-gate'+suffix+'/frozen-summary.json']})
    for key,description,source in [('group-failure','Real merge_group-only Actions failure ejected ordinary PR; trunk unchanged.','ci/RESULTS.md'),('queued-source-edit','Queued source exact-lease atomic update rejected GH006, archive also absent.','edit/RESULTS.md'),('admission-failure','Failing upper source check rejected selected-prefix admission before landing.','native/RESULTS.md'),('receipt-lifecycle','Original terminal enqueued UUID persisted after removal/landing.','RESULTS.md')]:rows.append({'id':'Q10-'+key,'disposition':'reused','why':'Settled direct control; no new discriminator requires repetition.','outcome':description,'evidence':[PRIOR+source]})
    result={'generated_at':now(),'cases':rows,'limitations':['Only tested configurations and observations; no permanent provider contract.','API intervals include deliberate pacing; they are client call envelopes, not exact server dispatch instants.','GraphQL confirmed upper/middle dequeue rejected based on direct base; actual UI removal is not established by that rejection.','Per-PR timestamps and branch observations expose outcomes, not transaction IDs or proof of no later provider writes.','Q06 ALLGREEN candidate failure stayed blocked during its measured interval and was manually cleaned; no automatic ejection claim.'],'audit':{k:audit[k] for k in ['start','end','queue_empty','archive_exact','patches_preserved','graphql_git_coherent','unresolved_intents','incomplete_actions']}}
    save(HOME/'case-matrix.json',result)
    table=[]
    for method in ['MERGE','SQUASH','REBASE']:
        vals=[]
        for strategy,build in [('ALLGREEN',1),('HEADGREEN',1),('ALLGREEN',2),('HEADGREEN',2)]:
            row=next(r for r in rows if r['id'].lower()=='q03-'+method.lower()+'-'+strategy.lower()+'-'+str(build))
            if row['disposition']=='reused':text=('AB merged' if method=='MERGE' else 'A merged; B ejected')+' (reused)'
            else:text='AB merged' if row['final_landed']==['A','B'] else 'A merged; B ejected'
            vals.append(text)
        table.append('| '+method+' | '+' | '.join(vals)+' |')
    (HOME/'METHOD-TABLE.md').write_text('\n'.join(table)+'\n')
    print(json.dumps({'cases':len(rows),'performed':sum(r['disposition']=='performed' for r in rows),'reused':sum(r['disposition']=='reused' for r in rows)}))
if __name__=='__main__':main()
